import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Activity, 
  HardDrive, 
  Settings2, 
  History, 
  ShieldCheck 
} from 'lucide-react';
import { cn } from '../utils/cn';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'System', href: '/system', icon: Activity },
  { name: 'Storage', href: '/storage', icon: HardDrive },
  { name: 'Tweaks', href: '/tweaks', icon: Settings2 },
  { name: 'History', href: '/history', icon: History },
];

export function Layout() {
  return (
    <div className="flex min-h-screen bg-gray-50 text-gray-900 font-sans">
      {/* Sidebar */}
      <aside className="fixed inset-y-0 left-0 w-64 border-r border-gray-200 bg-white shadow-sm z-30">
        <div className="flex h-16 items-center border-b border-gray-100 px-6">
          <ShieldCheck className="h-8 w-8 text-blue-600 mr-3" />
          <span className="text-xl font-bold tracking-tight text-gray-800">JOC Engine</span>
        </div>
        <nav className="mt-6 space-y-1 px-4">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                cn(
                  'group flex items-center rounded-lg px-4 py-2.5 text-sm font-medium transition-all duration-200',
                  isActive
                    ? 'bg-blue-50 text-blue-700 shadow-sm ring-1 ring-blue-100/50'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                )
              }
            >
              <item.icon className={cn('mr-3 h-5 w-5 transition-colors', 'text-gray-400 group-hover:text-blue-500')} />
              {item.name}
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 ml-64 p-8">
        <div className="mx-auto max-w-7xl">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
