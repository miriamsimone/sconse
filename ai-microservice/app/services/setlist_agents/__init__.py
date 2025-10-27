"""
Setlist Agents Package - Multi-Agent System for Concert Setlist Design
"""
from .base_agent import BaseSetlistAgent
from .music_curator_agent import MusicCuratorAgent
from .technical_advisor_agent import TechnicalAdvisorAgent
from .program_flow_agent import ProgramFlowAgent
from .multi_agent_coordinator import MultiAgentCoordinator

__all__ = [
    "BaseSetlistAgent",
    "MusicCuratorAgent", 
    "TechnicalAdvisorAgent",
    "ProgramFlowAgent",
    "MultiAgentCoordinator"
]
