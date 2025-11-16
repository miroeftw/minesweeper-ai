"""
Leaderboard system for tracking best Minesweeper games
"""

import json
import os
from datetime import datetime
from typing import List, Dict
from game.minesweeper import Difficulty

class LeaderboardEntry:
    def __init__(self, difficulty: str, time: int, date: str, player: str = "Player"):
        self.difficulty = difficulty
        self.time = time
        self.date = date
        self.player = player
    
    def to_dict(self) -> Dict:
        return {
            'difficulty': self.difficulty,
            'time': self.time,
            'date': self.date,
            'player': self.player
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'LeaderboardEntry':
        return LeaderboardEntry(
            difficulty=data['difficulty'],
            time=data['time'],
            date=data['date'],
            player=data.get('player', 'Player')
        )

class Leaderboard:
    def __init__(self, filename: str = 'leaderboard.json'):
        self.filename = filename
        self.entries: Dict[str, List[LeaderboardEntry]] = {
            'BEGINNER': [],
            'INTERMEDIATE': [],
            'EXPERT': []
        }
        self.load()
    
    def load(self):
        """Load leaderboard from file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    for difficulty, entries in data.items():
                        self.entries[difficulty] = [
                            LeaderboardEntry.from_dict(e) for e in entries
                        ]
            except Exception as e:
                print(f"Error loading leaderboard: {e}")
    
    def save(self):
        """Save leaderboard to file"""
        try:
            data = {}
            for difficulty, entries in self.entries.items():
                data[difficulty] = [e.to_dict() for e in entries]
            
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving leaderboard: {e}")
    
    def add_entry(self, difficulty: Difficulty, time: int, player: str = "Player"):
        """Add a new entry to the leaderboard"""
        difficulty_name = difficulty.name
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        entry = LeaderboardEntry(difficulty_name, time, date, player)
        self.entries[difficulty_name].append(entry)
        
        # Sort by time (ascending) and keep top 10
        self.entries[difficulty_name].sort(key=lambda x: x.time)
        self.entries[difficulty_name] = self.entries[difficulty_name][:10]
        
        self.save()
        
        # Return position (1-indexed)
        for i, e in enumerate(self.entries[difficulty_name], 1):
            if e.time == time and e.date == date:
                return i
        return None
    
    def get_top_entries(self, difficulty: Difficulty, limit: int = 10) -> List[LeaderboardEntry]:
        """Get top entries for a difficulty"""
        difficulty_name = difficulty.name
        return self.entries[difficulty_name][:limit]
    
    def get_best_time(self, difficulty: Difficulty) -> int:
        """Get best time for a difficulty"""
        entries = self.get_top_entries(difficulty, 1)
        return entries[0].time if entries else 999
    
    def is_top_score(self, difficulty: Difficulty, time: int) -> bool:
        """Check if time would make it to top 10"""
        difficulty_name = difficulty.name
        if len(self.entries[difficulty_name]) < 10:
            return True
        return time < self.entries[difficulty_name][-1].time