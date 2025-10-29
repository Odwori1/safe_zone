'use client';

import { useState } from 'react';
import { useUsersStore } from '@/stores/users-store';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { MoreHorizontal, Shield, Flag, UserX, UserCheck, Ban, AlertTriangle } from 'lucide-react';

interface UserActionsProps {
  userId: string;
  username: string;
  isBlocked?: boolean;
  onActionComplete?: () => void;
}

export function UserActions({ userId, username, isBlocked = false, onActionComplete }: UserActionsProps) {
  const [showReportDialog, setShowReportDialog] = useState(false);
  const [showBlockDialog, setShowBlockDialog] = useState(false);
  const [reportReason, setReportReason] = useState('');
  const [reportDetails, setReportDetails] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { 
    blockUser, 
    unblockUser, 
    reportUser, 
    blockLoading,
    reportLoading
  } = useUsersStore();

  const handleBlock = async () => {
    try {
      if (isBlocked) {
        await unblockUser(userId);
      } else {
        await blockUser(userId);
      }
      setShowBlockDialog(false);
      onActionComplete?.();
    } catch (error) {
      console.error('Failed to toggle block:', error);
    }
  };

  const handleReport = async () => {
    if (!reportReason.trim()) return;

    setIsSubmitting(true);
    try {
      await reportUser(userId, reportReason, reportDetails || undefined);
      setShowReportDialog(false);
      setReportReason('');
      setReportDetails('');
      onActionComplete?.();
    } catch (error) {
      console.error('Failed to report user:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const reportReasons = [
    'Harassment or bullying',
    'Hate speech',
    'Spam or scams', 
    'Inappropriate content',
    'Impersonation',
    'Threats of violence',
    'Self-harm content',
    'Other'
  ];

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" className="h-8 w-8 p-0">
            <span className="sr-only">Open menu</span>
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          {isBlocked ? (
            <DropdownMenuItem onClick={() => setShowBlockDialog(true)}>
              <UserCheck className="h-4 w-4 mr-2" />
              Unblock User
            </DropdownMenuItem>
          ) : (
            <DropdownMenuItem onClick={() => setShowBlockDialog(true)}>
              <Ban className="h-4 w-4 mr-2" />
              Block User
            </DropdownMenuItem>
          )}
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={() => setShowReportDialog(true)}>
            <Flag className="h-4 w-4 mr-2" />
            Report User
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Block/Unblock Dialog */}
      <Dialog open={showBlockDialog} onOpenChange={setShowBlockDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              {isBlocked ? 'Unblock User' : 'Block User'}
            </DialogTitle>
            <DialogDescription>
              {isBlocked 
                ? `Are you sure you want to unblock ${username}? You will be able to see their content and they will be able to interact with you again.`
                : `Are you sure you want to block ${username}? You won't see their content and they won't be able to interact with you.`
              }
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowBlockDialog(false)}
            >
              Cancel
            </Button>
            <Button
              variant={isBlocked ? "default" : "destructive"}
              onClick={handleBlock}
              disabled={blockLoading[userId]}
            >
              {blockLoading[userId] ? 'Processing...' : isBlocked ? 'Unblock' : 'Block'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Report Dialog */}
      <Dialog open={showReportDialog} onOpenChange={setShowReportDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              Report User
            </DialogTitle>
            <DialogDescription>
              Report {username} for violating community guidelines. 
              This report will be reviewed by our moderation team.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="report-reason">Reason for Report</Label>
              <select
                id="report-reason"
                value={reportReason}
                onChange={(e) => setReportReason(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Select a reason</option>
                {reportReasons.map((reason) => (
                  <option key={reason} value={reason}>
                    {reason}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="report-details">
                Additional Details {reportReason === 'Other' && '(Required)'}
              </Label>
              <Textarea
                id="report-details"
                placeholder={
                  reportReason === 'Other' 
                    ? 'Please provide specific details about your concern...'
                    : 'Provide any additional context or details (optional)...'
                }
                value={reportDetails}
                onChange={(e) => setReportDetails(e.target.value)}
                rows={4}
                required={reportReason === 'Other'}
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowReportDialog(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={handleReport}
              disabled={isSubmitting || !reportReason.trim() || (reportReason === 'Other' && !reportDetails.trim())}
              variant="destructive"
            >
              {isSubmitting ? 'Submitting...' : 'Submit Report'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
