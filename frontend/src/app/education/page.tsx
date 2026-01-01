'use client';

import Link from 'next/link';
import { useState } from 'react';

interface EducationSection {
  id: string;
  title: string;
  icon: string;
  content: React.ReactNode;
}

export default function EducationPage() {
  const [activeSection, setActiveSection] = useState<string>('basics');

  const sections: EducationSection[] = [
    {
      id: 'basics',
      title: 'NBA Betting Basics',
      icon: '🏀',
      content: (
        <div className="space-y-6">
          <div>
            <h3 className="text-2xl font-bold text-white mb-4">Understanding NBA Props</h3>
            <p className="text-gray-300 mb-4">
              NBA player props are bets on individual player statistics rather than game outcomes. 
              You're betting on whether a player will go over or under a specific statistical threshold.
            </p>
          </div>

          <div className="dashboard-card">
            <h4 className="text-xl font-semibold mb-3" style={{ color: 'var(--accent-green)' }}>Common Prop Types</h4>
            <ul className="space-y-3">
              <li className="flex items-start gap-3">
                <span className="text-green-400 text-xl">•</span>
                <div>
                  <strong className="text-white">Points (PTS):</strong>
                  <span className="text-gray-300"> Total points scored by a player in a game</span>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-green-400 text-xl">•</span>
                <div>
                  <strong className="text-white">Rebounds (REB):</strong>
                  <span className="text-gray-300"> Total rebounds (offensive + defensive) grabbed</span>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-green-400 text-xl">•</span>
                <div>
                  <strong className="text-white">Assists (AST):</strong>
                  <span className="text-gray-300"> Total assists distributed to teammates</span>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-green-400 text-xl">•</span>
                <div>
                  <strong className="text-white">Three-Pointers (3PM):</strong>
                  <span className="text-gray-300"> Number of three-point shots made</span>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-green-400 text-xl">•</span>
                <div>
                  <strong className="text-white">Combos (PRA, P+R, P+A):</strong>
                  <span className="text-gray-300"> Combined stats like Points + Rebounds + Assists</span>
                </div>
              </li>
            </ul>
          </div>

          <div className="dashboard-card" style={{ background: 'rgba(0, 255, 127, 0.05)', border: '1px solid rgba(0, 255, 127, 0.2)' }}>
            <h4 className="text-xl font-semibold mb-3" style={{ color: 'var(--accent-green)' }}>Key Tip</h4>
            <p className="text-gray-300">
              Always check if a player is starting vs. coming off the bench. Starting players typically get 
              more minutes and opportunities, which significantly impacts their ability to hit props.
            </p>
          </div>
        </div>
      )
    },
    {
      id: 'research',
      title: 'Research & Analysis',
      icon: '📊',
      content: (
        <div className="space-y-6">
          <div>
            <h3 className="text-2xl font-bold text-white mb-4">How to Research Player Props</h3>
            <p className="text-gray-300 mb-4">
              Successful prop betting requires analyzing multiple factors. Here's what to consider:
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="dashboard-card">
              <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <span style={{ color: 'var(--accent-green)' }}>📈</span>
                Recent Form
              </h4>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>• Review last 5-10 games</li>
                <li>• Look for trending patterns</li>
                <li>• Check home vs. away splits</li>
                <li>• Analyze minutes played</li>
              </ul>
            </div>

            <div className="dashboard-card">
              <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <span style={{ color: 'var(--accent-green)' }}>🏥</span>
                Injury Reports
              </h4>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>• Check official injury reports daily</li>
                <li>• Monitor load management</li>
                <li>• Consider teammate injuries (more usage)</li>
                <li>• Track return from injury performance</li>
              </ul>
            </div>

            <div className="dashboard-card">
              <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <span style={{ color: 'var(--accent-green)' }}>🛡️</span>
                Defensive Matchups
              </h4>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>• DVP (Defense vs. Position) rankings</li>
                <li>• Team defensive pace</li>
                <li>• Individual defender matchups</li>
                <li>• Historical performance vs. opponent</li>
              </ul>
            </div>

            <div className="dashboard-card">
              <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <span style={{ color: 'var(--accent-green)' }}>⚡</span>
                Game Context
              </h4>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>• Expected game pace/tempo</li>
                <li>• Projected point total</li>
                <li>• Back-to-back games</li>
                <li>• Rest days between games</li>
              </ul>
            </div>
          </div>

          <div className="dashboard-card" style={{ background: 'rgba(128, 0, 255, 0.05)', border: '1px solid rgba(128, 0, 255, 0.2)' }}>
            <h4 className="text-xl font-semibold mb-3" style={{ color: 'var(--accent-purple)' }}>Pro Strategy</h4>
            <p className="text-gray-300">
              Use our DVP (Defense vs. Position) data to identify favorable matchups. Teams that rank poorly 
              against specific positions often allow higher stats to those players. For example, if a team 
              ranks 28th against point guards, target PG props in that matchup.
            </p>
          </div>
        </div>
      )
    },
    {
      id: 'bankroll',
      title: 'Bankroll Management',
      icon: '💰',
      content: (
        <div className="space-y-6">
          <div>
            <h3 className="text-2xl font-bold text-white mb-4">Managing Your Betting Bankroll</h3>
            <p className="text-gray-300 mb-4">
              Proper bankroll management is the difference between long-term success and going broke. 
              Follow these principles from professional sports bettors:
            </p>
          </div>

          <div className="dashboard-card">
            <h4 className="text-xl font-semibold mb-4" style={{ color: 'var(--accent-green)' }}>The Unit System</h4>
            <p className="text-gray-300 mb-4">
              Professional bettors use a "unit" system where 1 unit = 1-2% of your total bankroll.
            </p>
            
            <div className="bg-black bg-opacity-30 p-4 rounded-lg mb-4">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-gray-400 text-sm mb-1">Bankroll</div>
                  <div className="text-2xl font-bold text-white">$1,000</div>
                </div>
                <div>
                  <div className="text-gray-400 text-sm mb-1">Unit Size (1%)</div>
                  <div className="text-2xl font-bold" style={{ color: 'var(--accent-green)' }}>$10</div>
                </div>
                <div>
                  <div className="text-gray-400 text-sm mb-1">Unit Size (2%)</div>
                  <div className="text-2xl font-bold" style={{ color: 'var(--accent-green)' }}>$20</div>
                </div>
              </div>
            </div>

            <ul className="space-y-2 text-gray-300">
              <li>• <strong className="text-white">Standard Bets:</strong> 1 unit</li>
              <li>• <strong className="text-white">High Confidence:</strong> 2-3 units</li>
              <li>• <strong className="text-white">Max Bet:</strong> Never exceed 5 units</li>
            </ul>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="dashboard-card" style={{ background: 'rgba(255, 107, 107, 0.05)', border: '1px solid rgba(255, 107, 107, 0.2)' }}>
              <h4 className="text-lg font-semibold mb-3" style={{ color: '#ff6b6b' }}>❌ Don'ts</h4>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>• Don't chase losses by increasing bet size</li>
                <li>• Don't bet more than you can afford to lose</li>
                <li>• Don't put entire bankroll on one bet</li>
                <li>• Don't bet under emotional influence</li>
                <li>• Don't skip tracking your bets</li>
              </ul>
            </div>

            <div className="dashboard-card" style={{ background: 'rgba(0, 255, 127, 0.05)', border: '1px solid rgba(0, 255, 127, 0.2)' }}>
              <h4 className="text-lg font-semibold mb-3" style={{ color: 'var(--accent-green)' }}>✅ Do's</h4>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>• Set a dedicated bankroll separate from expenses</li>
                <li>• Track all bets in a spreadsheet</li>
                <li>• Stick to your unit sizing system</li>
                <li>• Take breaks after losing streaks</li>
                <li>• Reassess bankroll monthly</li>
              </ul>
            </div>
          </div>

          <div className="dashboard-card">
            <h4 className="text-xl font-semibold mb-3" style={{ color: 'var(--accent-yellow)' }}>⚠️ The Golden Rule</h4>
            <p className="text-gray-300 text-lg">
              Never bet money you can't afford to lose. Sports betting should be entertainment with the 
              potential for profit, not a way to make rent money. If you're feeling stressed about losses, 
              take a break and reassess.
            </p>
          </div>
        </div>
      )
    },
    {
      id: 'odds',
      title: 'Understanding Odds & EV',
      icon: '🎯',
      content: (
        <div className="space-y-6">
          <div>
            <h3 className="text-2xl font-bold text-white mb-4">Reading Odds & Finding Value</h3>
            <p className="text-gray-300 mb-4">
              Understanding how to read odds and calculate Expected Value (EV) is crucial for profitable betting.
            </p>
          </div>

          <div className="dashboard-card">
            <h4 className="text-xl font-semibold mb-4" style={{ color: 'var(--accent-green)' }}>American Odds Explained</h4>
            
            <div className="grid md:grid-cols-2 gap-6 mb-4">
              <div className="bg-black bg-opacity-30 p-4 rounded-lg">
                <div className="text-lg font-bold mb-2" style={{ color: 'var(--accent-green)' }}>Negative Odds (-)</div>
                <div className="text-3xl font-bold text-white mb-2">-150</div>
                <p className="text-gray-300 text-sm mb-2">
                  Amount you need to bet to win $100
                </p>
                <div className="bg-black bg-opacity-50 p-3 rounded">
                  <div className="text-xs text-gray-400 mb-1">To win $100, bet:</div>
                  <div className="text-xl font-bold text-white">$150</div>
                  <div className="text-xs text-gray-400 mt-2">Implied Probability: 60%</div>
                </div>
              </div>

              <div className="bg-black bg-opacity-30 p-4 rounded-lg">
                <div className="text-lg font-bold mb-2" style={{ color: 'var(--accent-green)' }}>Positive Odds (+)</div>
                <div className="text-3xl font-bold text-white mb-2">+130</div>
                <p className="text-gray-300 text-sm mb-2">
                  Amount you win if you bet $100
                </p>
                <div className="bg-black bg-opacity-50 p-3 rounded">
                  <div className="text-xs text-gray-400 mb-1">Bet $100, win:</div>
                  <div className="text-xl font-bold text-white">$130</div>
                  <div className="text-xs text-gray-400 mt-2">Implied Probability: 43.5%</div>
                </div>
              </div>
            </div>
          </div>

          <div className="dashboard-card">
            <h4 className="text-xl font-semibold mb-4" style={{ color: 'var(--accent-purple)' }}>Expected Value (EV)</h4>
            <p className="text-gray-300 mb-4">
              EV is a mathematical calculation that tells you the expected profit or loss of a bet over the long run. 
              Positive EV (+EV) bets are profitable over time.
            </p>

            <div className="bg-black bg-opacity-30 p-5 rounded-lg mb-4">
              <div className="text-center mb-4">
                <div className="text-sm text-gray-400 mb-2">EV Formula</div>
                <div className="text-xl font-mono text-white">
                  EV = (Win Probability × Profit) - (Loss Probability × Stake)
                </div>
              </div>

              <div className="border-t border-gray-700 pt-4">
                <div className="text-sm font-semibold mb-2" style={{ color: 'var(--accent-yellow)' }}>Example:</div>
                <p className="text-gray-300 text-sm mb-3">
                  You believe LeBron has a 55% chance to score Over 25.5 points, but the odds are +100 (50% implied)
                </p>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="text-gray-400">Your Assessment:</div>
                    <div className="text-white font-semibold">55% chance to win</div>
                  </div>
                  <div>
                    <div className="text-gray-400">Sportsbook Odds:</div>
                    <div className="text-white font-semibold">+100 (50% implied)</div>
                  </div>
                </div>
                <div className="mt-3 p-3 rounded" style={{ background: 'rgba(0, 255, 127, 0.1)' }}>
                  <div className="text-sm text-gray-300">EV = (0.55 × $100) - (0.45 × $100)</div>
                  <div className="text-lg font-bold mt-1" style={{ color: 'var(--accent-green)' }}>
                    EV = +$10 per $100 bet (10% edge!)
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-black bg-opacity-30 p-4 rounded-lg">
              <h5 className="font-semibold mb-2 text-white">Finding +EV Bets:</h5>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>• Compare odds across multiple sportsbooks (line shopping)</li>
                <li>• Use statistical models to estimate true probability</li>
                <li>• Look for market inefficiencies (injury news, load management)</li>
                <li>• Track closing line value (CLV) - if you beat the closing line, you likely found value</li>
              </ul>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'injuries',
      title: 'Load Management & Injuries',
      icon: '🏥',
      content: (
        <div className="space-y-6">
          <div>
            <h3 className="text-2xl font-bold text-white mb-4">Navigating Injury News & Load Management</h3>
            <p className="text-gray-300 mb-4">
              The NBA is a star-driven league where one injury or rest day can dramatically shift betting lines. 
              Here's how to capitalize on this information:
            </p>
          </div>

          <div className="dashboard-card">
            <h4 className="text-xl font-semibold mb-4" style={{ color: 'var(--accent-green)' }}>Timing Your Bets</h4>
            
            <div className="space-y-4">
              <div className="bg-black bg-opacity-30 p-4 rounded-lg">
                <div className="flex items-start gap-3 mb-2">
                  <span className="text-2xl">⏰</span>
                  <div className="flex-1">
                    <h5 className="font-semibold text-white mb-2">Injury Reports Schedule</h5>
                    <ul className="space-y-2 text-gray-300 text-sm">
                      <li>• <strong className="text-white">5:00 PM ET:</strong> Initial injury reports released</li>
                      <li>• <strong className="text-white">90 mins before tip:</strong> Updated reports</li>
                      <li>• <strong className="text-white">30 mins before tip:</strong> Final injury report</li>
                      <li>• <strong className="text-white">Tip-off:</strong> Starting lineups confirmed</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-black bg-opacity-30 p-4 rounded-lg">
                  <h5 className="font-semibold mb-2 flex items-center gap-2">
                    <span style={{ color: 'var(--accent-green)' }}>✅</span>
                    <span className="text-white">Early Bird Strategy</span>
                  </h5>
                  <p className="text-gray-300 text-sm mb-2">
                    Lock in bets early when lines are released (usually 24-48 hours before game)
                  </p>
                  <div className="text-xs text-gray-400">
                    <strong>Pros:</strong> Beat line movements, less competition<br/>
                    <strong>Cons:</strong> Risk of late scratches
                  </div>
                </div>

                <div className="bg-black bg-opacity-30 p-4 rounded-lg">
                  <h5 className="font-semibold mb-2 flex items-center gap-2">
                    <span style={{ color: 'var(--accent-yellow)' }}>⚡</span>
                    <span className="text-white">Late News Strategy</span>
                  </h5>
                  <p className="text-gray-300 text-sm mb-2">
                    Wait for final injury reports and starting lineups before betting
                  </p>
                  <div className="text-xs text-gray-400">
                    <strong>Pros:</strong> Complete information, no surprises<br/>
                    <strong>Cons:</strong> Lines may have moved, less value
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="dashboard-card" style={{ background: 'rgba(128, 0, 255, 0.05)', border: '1px solid rgba(128, 0, 255, 0.2)' }}>
            <h4 className="text-xl font-semibold mb-4" style={{ color: 'var(--accent-purple)' }}>Understanding Load Management</h4>
            <p className="text-gray-300 mb-4">
              Load management is when teams rest healthy players to preserve them for playoffs or prevent injuries.
            </p>

            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <span className="text-xl">📅</span>
                <div>
                  <strong className="text-white">Back-to-Backs:</strong>
                  <p className="text-gray-300 text-sm">Many stars sit the second game of back-to-back sets. Check the schedule!</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-xl">✈️</span>
                <div>
                  <strong className="text-white">Road Trip Games:</strong>
                  <p className="text-gray-300 text-sm">Late in long road trips, teams may rest veterans (3rd or 4th game in 5 nights)</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-xl">👴</span>
                <div>
                  <strong className="text-white">Veteran Players:</strong>
                  <p className="text-gray-300 text-sm">Players 30+ or with injury history are prime candidates for rest days</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-xl">🗓️</span>
                <div>
                  <strong className="text-white">Season Timing:</strong>
                  <p className="text-gray-300 text-sm">More load management in March/April as playoffs approach</p>
                </div>
              </div>
            </div>
          </div>

          <div className="dashboard-card">
            <h4 className="text-xl font-semibold mb-4" style={{ color: 'var(--accent-green)' }}>Capitalizing on Injuries</h4>
            
            <div className="bg-black bg-opacity-30 p-4 rounded-lg">
              <h5 className="font-semibold text-white mb-3">When a Star is Out:</h5>
              <div className="space-y-3 text-gray-300 text-sm">
                <div className="flex items-start gap-2">
                  <span className="text-green-400 mt-1">→</span>
                  <div>
                    <strong className="text-white">Usage Rate Increases:</strong> Remaining players handle more possessions
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-green-400 mt-1">→</span>
                  <div>
                    <strong className="text-white">Target Role Players:</strong> Backup PG or SG often sees biggest bump
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-green-400 mt-1">→</span>
                  <div>
                    <strong className="text-white">Check Historical Data:</strong> How did team perform without this player before?
                  </div>
                </div>
              </div>

              <div className="mt-4 p-3 rounded" style={{ background: 'rgba(0, 255, 127, 0.1)' }}>
                <div className="text-sm font-semibold mb-1" style={{ color: 'var(--accent-green)' }}>Example Scenario:</div>
                <p className="text-gray-300 text-sm">
                  Stephen Curry (Out) → Jordan Poole's usage jumps from 25% to 32%, his assists typically increase by 2-3. 
                  His props may not adjust fast enough, creating value.
                </p>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'tips',
      title: 'Advanced Tips',
      icon: '🎓',
      content: (
        <div className="space-y-6">
          <div>
            <h3 className="text-2xl font-bold text-white mb-4">Pro-Level Betting Strategies</h3>
            <p className="text-gray-300 mb-4">
              Take your betting to the next level with these advanced concepts used by professional sports bettors:
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="dashboard-card">
              <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <span style={{ color: 'var(--accent-green)' }}>🔍</span>
                Line Shopping
              </h4>
              <p className="text-gray-300 text-sm mb-3">
                Different sportsbooks offer different lines. Always compare before betting.
              </p>
              <div className="bg-black bg-opacity-30 p-3 rounded text-sm">
                <div className="font-semibold text-white mb-2">Example:</div>
                <div className="space-y-1 text-gray-300">
                  <div>Sportsbook A: LeBron Over 26.5 (-110)</div>
                  <div>Sportsbook B: LeBron Over 25.5 (-110)</div>
                  <div className="pt-2 border-t border-gray-700 mt-2" style={{ color: 'var(--accent-green)' }}>
                    → Choose B for a full point of value!
                  </div>
                </div>
              </div>
            </div>

            <div className="dashboard-card">
              <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <span style={{ color: 'var(--accent-green)' }}>📉</span>
                Regression to the Mean
              </h4>
              <p className="text-gray-300 text-sm mb-3">
                Players who overperform or underperform tend to return to their averages.
              </p>
              <div className="bg-black bg-opacity-30 p-3 rounded text-sm text-gray-300">
                If a 15 PPG scorer has 3 straight 25+ point games, consider betting the under. 
                Conversely, if they've had 3 straight single-digit games, the over may have value.
              </div>
            </div>

            <div className="dashboard-card">
              <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <span style={{ color: 'var(--accent-green)' }}>🏃</span>
                Pace & Tempo
              </h4>
              <p className="text-gray-300 text-sm mb-3">
                Faster-paced games = more possessions = more stats
              </p>
              <div className="bg-black bg-opacity-30 p-3 rounded text-sm">
                <div className="text-gray-300 mb-2">Top 5 Fastest Teams (2025-26):</div>
                <div className="space-y-1 text-gray-400">
                  <div>1. Kings - 103.2 possessions/game</div>
                  <div>2. Pacers - 102.8 possessions/game</div>
                  <div>3. Warriors - 101.5 possessions/game</div>
                </div>
                <div className="pt-2 mt-2 border-t border-gray-700 text-gray-300">
                  Target overs when these teams play each other!
                </div>
              </div>
            </div>

            <div className="dashboard-card">
              <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <span style={{ color: 'var(--accent-green)' }}>🎯</span>
                Alternate Lines
              </h4>
              <p className="text-gray-300 text-sm mb-3">
                Consider taking alternate lines for better odds if you're very confident
              </p>
              <div className="bg-black bg-opacity-30 p-3 rounded text-sm">
                <div className="space-y-2 text-gray-300">
                  <div>Standard: Over 25.5 points (-110)</div>
                  <div>Alt Line: Over 23.5 points (-175)</div>
                  <div>Alt Line: Over 27.5 points (+130)</div>
                </div>
                <div className="pt-2 mt-2 border-t border-gray-700" style={{ color: 'var(--accent-yellow)' }}>
                  If very confident: Take lower line despite worse odds for higher win probability
                </div>
              </div>
            </div>

            <div className="dashboard-card">
              <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <span style={{ color: 'var(--accent-green)' }}>📊</span>
                Correlation Betting
              </h4>
              <p className="text-gray-300 text-sm mb-3">
                Some stats are correlated - use this to your advantage in parlays
              </p>
              <div className="bg-black bg-opacity-30 p-3 rounded text-sm text-gray-300">
                <div className="mb-2">Positive Correlations:</div>
                <div>• High points usually means high FG attempts</div>
                <div>• High rebounds often correlates with blocks (bigs)</div>
                <div className="mt-3 mb-2">Negative Correlations:</div>
                <div>• High assists + high points (ball dominant guards)</div>
                <div>• High usage + high efficiency (harder to maintain)</div>
              </div>
            </div>

            <div className="dashboard-card">
              <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <span style={{ color: 'var(--accent-green)' }}>⏱️</span>
                Minutes Played Threshold
              </h4>
              <p className="text-gray-300 text-sm mb-3">
                Most props require ~28+ minutes to have a good chance of hitting
              </p>
              <div className="bg-black bg-opacity-30 p-3 rounded text-sm text-gray-300">
                Check recent minutes trends. If a player averaged 35 mins but only played 25 last game, 
                investigate why. Blowouts? Foul trouble? Coach decision? This impacts prop viability.
              </div>
            </div>
          </div>

          <div className="dashboard-card" style={{ background: 'rgba(0, 255, 127, 0.05)', border: '1px solid rgba(0, 255, 127, 0.2)' }}>
            <h4 className="text-xl font-semibold mb-4" style={{ color: 'var(--accent-green)' }}>🏆 The Winning Mindset</h4>
            <div className="space-y-3 text-gray-300">
              <p>
                <strong className="text-white">Long-term thinking:</strong> You won't win every bet. Professional bettors aim for 
                52-55% win rate. Focus on making +EV bets consistently.
              </p>
              <p>
                <strong className="text-white">Track everything:</strong> Keep a detailed spreadsheet of all bets including 
                reasoning, odds, stake, and result. This helps identify what works.
              </p>
              <p>
                <strong className="text-white">Specialize:</strong> Rather than betting everything, focus on specific props 
                or teams you know deeply. Expertise creates edge.
              </p>
              <p>
                <strong className="text-white">Stay disciplined:</strong> Stick to your unit sizing even during hot streaks. 
                Variance will catch up if you get reckless.
              </p>
            </div>
          </div>
        </div>
      )
    }
  ];

  const activeContent = sections.find(s => s.id === activeSection);

  return (
    <div className="min-h-screen" style={{ background: 'var(--bg-dark)' }}>
      {/* Hero Section */}
      <div className="relative overflow-hidden" style={{ 
        background: 'linear-gradient(135deg, #101a13 0%, #1a2820 50%, #101a13 100%)',
        borderBottom: '1px solid rgba(0, 255, 127, 0.2)'
      }}>
        <div className="max-w-7xl mx-auto px-4 py-16 sm:py-24">
          <div className="text-center">
            <div className="mb-4">
              <Link 
                href="/props" 
                className="inline-flex items-center text-gray-400 hover:text-green-400 transition-colors"
              >
                ← Back to Props
              </Link>
            </div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-6">
              NBA Betting <span style={{ color: 'var(--accent-green)' }}>Education</span>
            </h1>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Master NBA player props with data-driven strategies, bankroll management, 
              and insights from professional sports bettors
            </p>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="sticky top-0 z-10" style={{ 
        background: 'var(--bg-card)',
        borderBottom: '1px solid rgba(0, 255, 127, 0.15)',
        backdropFilter: 'blur(10px)'
      }}>
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex overflow-x-auto scrollbar-hide">
            {sections.map((section) => (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={`flex items-center gap-2 px-6 py-4 font-semibold whitespace-nowrap transition-all ${
                  activeSection === section.id
                    ? 'text-white border-b-2'
                    : 'text-gray-400 hover:text-gray-300'
                }`}
                style={{
                  borderColor: activeSection === section.id ? 'var(--accent-green)' : 'transparent'
                }}
              >
                <span className="text-xl">{section.icon}</span>
                {section.title}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content Section */}
      <div className="max-w-7xl mx-auto px-4 py-12">
        {activeContent?.content}
      </div>

      {/* CTA Section */}
      <div className="max-w-7xl mx-auto px-4 py-16">
        <div className="dashboard-card text-center" style={{ 
          background: 'linear-gradient(135deg, rgba(0, 255, 127, 0.1) 0%, rgba(128, 0, 255, 0.1) 100%)',
          border: '1px solid rgba(0, 255, 127, 0.3)'
        }}>
          <h3 className="text-2xl font-bold text-white mb-4">Ready to Start Betting Smarter?</h3>
          <p className="text-gray-300 mb-6 max-w-2xl mx-auto">
            Access our full suite of analytics, DVP data, injury reports, and AI-powered predictions 
            to gain an edge on your NBA props.
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <Link href="/props" className="btn-primary btn-large">
              Browse Props
            </Link>
            <Link href="/pricing" className="btn-secondary btn-large">
              View Pricing
            </Link>
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="max-w-7xl mx-auto px-4 pb-12">
        <div className="text-center text-sm text-gray-500">
          <p>
            ⚠️ Gambling involves risk. Bet responsibly. If you or someone you know has a gambling problem, 
            call 1-800-GAMBLER.
          </p>
          <p className="mt-2">
            This educational content is for informational purposes only and does not guarantee profits. 
            Always do your own research.
          </p>
        </div>
      </div>
    </div>
  );
}