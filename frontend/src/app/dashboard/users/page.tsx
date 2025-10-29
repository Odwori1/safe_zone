'use client';

import UserSearch from '@/components/users/user-search';
import { Users } from 'lucide-react';

export default function UsersPage() {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg border p-6">
        <div className="flex items-center gap-3 mb-2">
          <Users className="h-8 w-8 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">Find Users</h1>
        </div>
        <p className="text-gray-600">
          Connect with other members of the Safe Zone community. Search for users by username, 
          name, or email to build your support network.
        </p>
      </div>

      <UserSearch />
    </div>
  );
}
