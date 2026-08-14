import React, { useState } from 'react';
import { 
  ShieldAlert, 
  CheckCircle2, 
  AlertTriangle, 
  Activity, 
  UserCheck, 
  Wrench, 
  Clock, 
  Send,
  ChevronDown,
  ChevronRight
} from 'lucide-react';
import { TimelineEvent } from '../../types';
import { incidentsService } from '../../services/incidents';

interface AttackTimelineProps {
  incidentId: string;
  timeline: TimelineEvent[];
  onEventAdded?: () => void;
  canEdit?: boolean;
}

export const AttackTimeline: React.FC<AttackTimelineProps> = ({
  incidentId,
  timeline = [],
  onEventAdded,
  canEdit = true
}) => {
  const [newNote, setNewNote] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [expandedEvents, setExpandedEvents] = useState<Record<string, boolean>>({});

  const toggleExpand = (id: string) => {
    setExpandedEvents((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNote.trim()) return;

    setIsSubmitting(true);
    try {
      await incidentsService.addTimelineEvent(incidentId, {
        event_type: 'ANALYST_ACTION',
        title: 'Analyst Investigation Note',
        description: newNote.trim()
      });
      setNewNote('');
      if (onEventAdded) onEventAdded();
    } catch (err) {
      console.error('Failed to append timeline event:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getEventIcon = (type: string) => {
    switch (type.toUpperCase()) {
      case 'DETECTION':
        return <ShieldAlert className="w-4 h-4 text-red-400" />;
      case 'ALERT_CORRELATED':
        return <AlertTriangle className="w-4 h-4 text-amber-400" />;
      case 'TRIAGE':
        return <Activity className="w-4 h-4 text-cyan-400" />;
      case 'STATUS_CHANGE':
        return <CheckCircle2 className="w-4 h-4 text-blue-400" />;
      case 'ANALYST_ACTION':
        return <UserCheck className="w-4 h-4 text-purple-400" />;
      case 'REMEDIATION':
        return <Wrench className="w-4 h-4 text-emerald-400" />;
      case 'RESOLUTION':
        return <CheckCircle2 className="w-4 h-4 text-emerald-400" />;
      default:
        return <Clock className="w-4 h-4 text-slate-400" />;
    }
  };

  const getEventBadgeColor = (type: string) => {
    switch (type.toUpperCase()) {
      case 'DETECTION':
        return 'bg-red-500/10 border-red-500/30 text-red-400';
      case 'ALERT_CORRELATED':
        return 'bg-amber-500/10 border-amber-500/30 text-amber-400';
      case 'TRIAGE':
        return 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400';
      case 'STATUS_CHANGE':
        return 'bg-blue-500/10 border-blue-500/30 text-blue-400';
      case 'ANALYST_ACTION':
        return 'bg-purple-500/10 border-purple-500/30 text-purple-400';
      case 'REMEDIATION':
        return 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400';
      default:
        return 'bg-slate-500/10 border-slate-500/30 text-slate-400';
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm">
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-cyan-500/10 border border-cyan-500/30 rounded-xl text-cyan-400">
            <Clock className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100 font-mono tracking-wide">
              ATTACK TIMELINE & INCIDENT AUDIT
            </h3>
            <p className="text-xs text-slate-400">
              Chronological order of telemetry detections, correlated alerts, analyst triage, and containment.
            </p>
          </div>
        </div>
        <span className="text-xs font-mono text-cyan-400 px-3 py-1 bg-cyan-950/60 border border-cyan-800/60 rounded-full">
          {timeline.length} Events
        </span>
      </div>

      {/* Timeline Stream */}
      <div className="relative pl-6 space-y-6 before:content-[''] before:absolute before:top-2 before:bottom-2 before:left-[11px] before:w-[2px] before:bg-gradient-to-b before:from-cyan-500 before:via-blue-500/40 before:to-slate-800">
        {timeline.length === 0 ? (
          <div className="text-center py-8 text-slate-500 text-xs font-mono">
            No timeline events recorded yet.
          </div>
        ) : (
          timeline.map((event) => {
            const isExpanded = !!expandedEvents[event.id];
            const hasMetadata = event.metadata_payload && Object.keys(event.metadata_payload).length > 0;

            return (
              <div key={event.id} className="relative group">
                {/* Node Dot */}
                <div className="absolute -left-[30px] top-1 w-5 h-5 rounded-full bg-slate-950 border-2 border-cyan-500 flex items-center justify-center shadow-lg shadow-cyan-500/20 group-hover:scale-110 transition-transform">
                  <div className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                </div>

                {/* Event Card */}
                <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4 transition-all duration-200 hover:border-slate-700 hover:bg-slate-900/60">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                    <div className="flex items-center space-x-2">
                      <span className={`inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-md text-[11px] font-bold border ${getEventBadgeColor(event.event_type)}`}>
                        {getEventIcon(event.event_type)}
                        <span>{event.event_type}</span>
                      </span>
                      <h4 className="text-sm font-semibold text-slate-200">
                        {event.title}
                      </h4>
                    </div>
                    <div className="flex items-center space-x-2 text-xs text-slate-400 font-mono">
                      <span>{new Date(event.timestamp).toLocaleString()}</span>
                      <span className="text-slate-600">•</span>
                      <span className="text-cyan-400 font-medium">@{event.actor}</span>
                    </div>
                  </div>

                  {event.description && (
                    <p className="text-xs text-slate-300 leading-relaxed mt-1">
                      {event.description}
                    </p>
                  )}

                  {hasMetadata && (
                    <div className="mt-3 pt-2 border-t border-slate-800/50">
                      <button
                        onClick={() => toggleExpand(event.id)}
                        className="flex items-center space-x-1 text-[11px] text-cyan-400 hover:text-cyan-300 transition-colors font-mono cursor-pointer"
                      >
                        {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                        <span>{isExpanded ? 'Hide Raw Metadata' : 'View Raw Telemetry Payload'}</span>
                      </button>
                      {isExpanded && (
                        <pre className="mt-2 p-2.5 bg-slate-950 rounded-lg border border-slate-800 text-[11px] font-mono text-cyan-300 overflow-x-auto">
                          {JSON.stringify(event.metadata_payload, null, 2)}
                        </pre>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Analyst Note Input */}
      {canEdit && (
        <form onSubmit={handleAddNote} className="mt-8 pt-4 border-t border-slate-800">
          <label className="block text-xs font-mono text-slate-400 uppercase tracking-wider mb-2">
            Append Analyst Note to Timeline:
          </label>
          <div className="flex items-center space-x-3">
            <input
              type="text"
              value={newNote}
              onChange={(e) => setNewNote(e.target.value)}
              placeholder="e.g. Verified malicious payload pattern, isolating compromised subnet..."
              disabled={isSubmitting}
              className="flex-1 bg-slate-950/80 border border-slate-800 focus:border-cyan-500 rounded-xl px-4 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-cyan-500 transition-all font-sans"
            />
            <button
              type="submit"
              disabled={isSubmitting || !newNote.trim()}
              className="px-4 py-2.5 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold font-mono transition-all flex items-center space-x-2 shadow-lg shadow-cyan-600/20 cursor-pointer"
            >
              <Send className="w-3.5 h-3.5" />
              <span>{isSubmitting ? 'Posting...' : 'Add Note'}</span>
            </button>
          </div>
        </form>
      )}
    </div>
  );
};
