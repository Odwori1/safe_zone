'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  Home, 
  Users, 
  BookOpen, 
  BarChart3, 
  MessageCircle,
  Settings 
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navigationItems = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: Home,
  },
  {
    name: 'Find Users',
    href: '/dashboard/users',
    icon: Users,
  },
  {
    name: 'Journals',
    href: '/dashboard/journals',
    icon: BookOpen,
  },
  {
    name: 'Mood Tracking',
    href: '/dashboard/mood',
    icon: BarChart3,
  },
  {
    name: 'Messages',
    href: '/dashboard/messages',
    icon: MessageCircle,
  },
  {
    name: 'Settings',
    href: '/dashboard/settings',
    icon: Settings,
  },
];

export default function Navigation() {
  const pathname = usePathname();

  return (
    <nav className="space-y-2">
      {navigationItems.map((item) => {
        const isActive = pathname === item.href;
        return (
          <Link
            key={item.name}
            href={item.href}
            className={cn(
              'flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
              isActive
                ? 'bg-blue-100 text-blue-700 border border-blue-200'
                : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
            )}
          >
            <item.icon className="w-4 h-4" />
            <span>{item.name}</span>
          </Link>
        );
      })}
    </nav>
  );
}
