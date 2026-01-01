import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models import User, SubscriptionTier, SubscriptionStatus
from app.schemas import CheckoutSessionResponse, PortalSessionResponse, SubscriptionResponse
from app.auth import get_current_active_user
from app.config import settings

router = APIRouter(prefix="/payments", tags=["Payments"])

# Initialize Stripe (optional - will work without it)
STRIPE_ENABLED = bool(settings.stripe_secret_key and settings.stripe_secret_key != "sk_test_your_stripe_secret_key")
if STRIPE_ENABLED:
    stripe.api_key = settings.stripe_secret_key


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a Stripe checkout session for subscription"""
    if not STRIPE_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payments are not configured yet. Contact support."
        )
    try:
        # Create or get Stripe customer
        if not current_user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                name=current_user.full_name,
                metadata={"user_id": current_user.id}
            )
            current_user.stripe_customer_id = customer.id
            db.commit()
        
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=current_user.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": settings.stripe_price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=f"{settings.frontend_url}/dashboard?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.frontend_url}/pricing",
            metadata={"user_id": current_user.id}
        )
        
        return CheckoutSessionResponse(
            checkout_url=checkout_session.url,
            session_id=checkout_session.id
        )
    
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/create-portal-session", response_model=PortalSessionResponse)
async def create_portal_session(
    current_user: User = Depends(get_current_active_user)
):
    """Create a Stripe customer portal session for managing subscription"""
    if not STRIPE_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payments are not configured yet. Contact support."
        )
    if not current_user.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No billing account found"
        )
    
    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=current_user.stripe_customer_id,
            return_url=f"{settings.frontend_url}/dashboard"
        )
        
        return PortalSessionResponse(portal_url=portal_session.url)
    
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(current_user: User = Depends(get_current_active_user)):
    """Get current user's subscription status"""
    return SubscriptionResponse(
        subscription_id=current_user.subscription_id or "",
        status=current_user.subscription_status or "none",
        current_period_end=current_user.subscription_end_date or datetime.utcnow(),
        tier=current_user.subscription_tier
    )


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        await handle_checkout_completed(session, db)
    
    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        await handle_subscription_updated(subscription, db)
    
    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        await handle_subscription_deleted(subscription, db)
    
    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        await handle_payment_failed(invoice, db)
    
    return {"status": "success"}


async def handle_checkout_completed(session: dict, db: Session):
    """Handle successful checkout"""
    customer_id = session.get("customer")
    subscription_id = session.get("subscription")
    
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if user:
        # Get subscription details
        subscription = stripe.Subscription.retrieve(subscription_id)
        
        user.subscription_id = subscription_id
        user.subscription_tier = SubscriptionTier.PRO  # Or determine from price
        user.subscription_status = subscription.status
        user.subscription_end_date = datetime.fromtimestamp(subscription.current_period_end)
        
        db.commit()


async def handle_subscription_updated(subscription: dict, db: Session):
    """Handle subscription updates"""
    customer_id = subscription.get("customer")
    
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if user:
        user.subscription_status = subscription.get("status")
        user.subscription_end_date = datetime.fromtimestamp(subscription.get("current_period_end"))
        
        # Handle cancellation
        if subscription.get("cancel_at_period_end"):
            user.subscription_status = SubscriptionStatus.CANCELED
        
        db.commit()


async def handle_subscription_deleted(subscription: dict, db: Session):
    """Handle subscription cancellation"""
    customer_id = subscription.get("customer")
    
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if user:
        user.subscription_tier = SubscriptionTier.FREE
        user.subscription_status = None
        user.subscription_id = None
        user.subscription_end_date = None
        
        db.commit()


async def handle_payment_failed(invoice: dict, db: Session):
    """Handle failed payment"""
    customer_id = invoice.get("customer")
    
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if user:
        user.subscription_status = SubscriptionStatus.PAST_DUE
        db.commit()
