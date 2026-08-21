# Phase 49: Autonomous Control Plane — Frontend Documentation

## Component Overview
The Command Control Plane is built at `frontend/src/pages/AutonomousControlPlaneCenter.tsx` and available on the `/control-plane` route in the application router.

## Key Sections & Tabs

### 1. Apex Scorecard
- Real-time display of Autonomy Posture Score (98.6%), Active Defense Missions, Multi-Agent Consensus Velocity (18.4ms), and Emergency Kill Switch state.
- Red pulsing Kill-Switch toggle button for manual operator override.

### 2. Tabs
- **Autonomous Missions Tab**: Grid of active missions with threat tier tags (Nation-State to Low), blast radius financial caps ($50K USD), human veto countdown timers, and dispatched action timelines.
- **Decisive War Rooms Tab**: Live multi-agent incident session view showing participating AI agents (IAM, Microseg, UEBA, SOAR), consensus confidence gauges, and tactical intervention dispatch buttons.
- **Tactical Decisions Tab**: Audit log of all autonomous containment actions executed across network and cloud infrastructure.
