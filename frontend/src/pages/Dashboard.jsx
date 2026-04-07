import React from 'react';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { 
  Activity, 
  HardDrive, 
  Zap, 
  Clock, 
  AlertTriangle, 
  ArrowRight 
} from 'lucide-react';
import { Link } from 'react-router-dom';

export function Dashboard() {
  const stats = [
    { name: 'System Health', value: 'Optimal', icon: Activity, color: 'text-green-600', bg: 'bg-green-100' },
    { name: 'Storage Free', value: '45 GB', icon: HardDrive, color: 'text-blue-600', bg: 'bg-blue-100' },
    { name: 'Active Tweaks', value: '3', icon: Zap, color: 'text-amber-600', bg: 'bg-amber-100' },
    { name: 'Last Scan', value: '2 hours ago', icon: Clock, color: 'text-purple-600', bg: 'bg-purple-100' },
  ];

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-3xl font-bold tracking-tight text-gray-900">System Dashboard</h1>
        <p className="mt-2 text-lg text-gray-600">Welcome back to JOC Engine. Here's your system status at a glance.</p>
      </header>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.name} className="flex items-center rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <div className={`mr-4 rounded-lg ${stat.bg} p-3`}>
              <stat.icon className={`h-6 w-6 ${stat.color}`} />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">{stat.name}</p>
              <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
        {/* Quick Actions */}
        <Card title="Quick Actions" description="Commonly used system maintenance tasks">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Link to="/system">
              <Button variant="outline" className="w-full justify-between group">
                Analyze System
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Button>
            </Link>
            <Link to="/storage">
              <Button variant="outline" className="w-full justify-between group">
                Scan Storage
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Button>
            </Link>
            <Link to="/tweaks">
              <Button variant="outline" className="w-full justify-between group">
                Optimize Performance
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Button>
            </Link>
            <Link to="/history">
              <Button variant="outline" className="w-full justify-between group">
                View History
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Button>
            </Link>
          </div>
        </Card>

        {/* Recent Alerts */}
        <Card title="Recent Alerts" description="Issues detected by the engine">
          <div className="space-y-4">
            <div className="flex items-start gap-4 rounded-lg bg-amber-50 p-4 ring-1 ring-amber-100">
              <AlertTriangle className="mt-0.5 h-5 w-5 text-amber-600" />
              <div>
                <h4 className="font-semibold text-amber-900">High Memory Usage</h4>
                <p className="mt-1 text-sm text-amber-800/80">Chrome is using more than 2GB of RAM. Consider closing unused tabs.</p>
              </div>
            </div>
            <div className="flex items-start gap-4 rounded-lg bg-blue-50 p-4 ring-1 ring-blue-100">
              <Activity className="mt-0.5 h-5 w-5 text-blue-600" />
              <div>
                <h4 className="font-semibold text-blue-900">Optimization Available</h4>
                <p className="mt-1 text-sm text-blue-800/80">3 system tweaks can be applied to improve gaming performance.</p>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
