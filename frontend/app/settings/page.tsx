'use client';

import React, { useState } from 'react';
import { BudgetLayout } from '@/components/layout/budget-layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import { 
  Settings, 
  Database, 
  Bell, 
  Shield, 
  Palette,
  Server,
  Download,
  RefreshCw,
  Check,
  AlertTriangle
} from 'lucide-react';

export default function SettingsPage() {
  const [apiUrl, setApiUrl] = useState('http://localhost:8000/api');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState('30');
  const [notifications, setNotifications] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const [defaultFiscalYear, setDefaultFiscalYear] = useState('2024-25');
  
  const handleSaveSettings = () => {
    // Save settings to localStorage or backend
    localStorage.setItem('budget-dashboard-settings', JSON.stringify({
      apiUrl,
      autoRefresh,
      refreshInterval,
      notifications,
      darkMode,
      defaultFiscalYear,
    }));
    
    alert('Settings saved successfully!');
  };

  const handleTestConnection = async () => {
    try {
      const response = await fetch(`${apiUrl}/health/`);
      if (response.ok) {
        alert('Connection successful!');
      } else {
        alert('Connection failed!');
      }
    } catch (error) {
      alert('Connection failed: ' + error.message);
    }
  };

  return (
    <BudgetLayout>
      <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      {/* Header */}
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Settings</h2>
        <div className="flex items-center space-x-2">
          <Button onClick={handleSaveSettings} size="sm">
            <Check className="h-4 w-4 mr-2" />
            Save Changes
          </Button>
        </div>
      </div>

      <Tabs defaultValue="general" className="space-y-4">
        <TabsList>
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="data">Data Sources</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="appearance">Appearance</TabsTrigger>
        </TabsList>

        {/* General Settings */}
        <TabsContent value="general" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                General Configuration
              </CardTitle>
              <CardDescription>
                Basic settings for the budget dashboard system
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="fiscal-year">Default Fiscal Year</Label>
                <Select value={defaultFiscalYear} onValueChange={setDefaultFiscalYear}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="2024-25">2024-25</SelectItem>
                    <SelectItem value="2023-24">2023-24</SelectItem>
                    <SelectItem value="2022-23">2022-23</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Auto Refresh Data</Label>
                  <p className="text-sm text-muted-foreground">
                    Automatically refresh data at specified intervals
                  </p>
                </div>
                <Switch checked={autoRefresh} onCheckedChange={setAutoRefresh} />
              </div>

              {autoRefresh && (
                <div className="space-y-2">
                  <Label htmlFor="refresh-interval">Refresh Interval (seconds)</Label>
                  <Select value={refreshInterval} onValueChange={setRefreshInterval}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="10">10 seconds</SelectItem>
                      <SelectItem value="30">30 seconds</SelectItem>
                      <SelectItem value="60">1 minute</SelectItem>
                      <SelectItem value="300">5 minutes</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Data Sources */}
        <TabsContent value="data" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                API Configuration
              </CardTitle>
              <CardDescription>
                Configure connection to the backend data services
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="api-url">Backend API URL</Label>
                <div className="flex space-x-2">
                  <Input
                    id="api-url"
                    value={apiUrl}
                    onChange={(e) => setApiUrl(e.target.value)}
                    placeholder="http://localhost:8000/api"
                    className="flex-1"
                  />
                  <Button onClick={handleTestConnection} variant="outline">
                    <Server className="h-4 w-4 mr-2" />
                    Test
                  </Button>
                </div>
                <p className="text-sm text-muted-foreground">
                  URL of the GovHack backend API service
                </p>
              </div>

              <Separator />

              <div className="space-y-4">
                <h4 className="font-medium">Data Source Status</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 border rounded">
                    <div className="flex items-center space-x-3">
                      <Database className="h-5 w-5 text-blue-500" />
                      <div>
                        <p className="font-medium">Budget Dataset (2024-25)</p>
                        <p className="text-sm text-muted-foreground">1,874 records</p>
                      </div>
                    </div>
                    <Badge variant="default">Active</Badge>
                  </div>

                  <div className="flex items-center justify-between p-3 border rounded">
                    <div className="flex items-center space-x-3">
                      <Database className="h-5 w-5 text-green-500" />
                      <div>
                        <p className="font-medium">PBS Data</p>
                        <p className="text-sm text-muted-foreground">856 records</p>
                      </div>
                    </div>
                    <Badge variant="default">Active</Badge>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notifications */}
        <TabsContent value="notifications" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5" />
                Notification Preferences
              </CardTitle>
              <CardDescription>
                Configure alerts and notification settings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Enable Notifications</Label>
                  <p className="text-sm text-muted-foreground">
                    Receive notifications for data updates and errors
                  </p>
                </div>
                <Switch checked={notifications} onCheckedChange={setNotifications} />
              </div>

              <Separator />

              <div className="space-y-4">
                <h4 className="font-medium">Notification Types</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Data Update Alerts</Label>
                      <p className="text-sm text-muted-foreground">
                        Notify when new data is available
                      </p>
                    </div>
                    <Switch defaultChecked />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Error Notifications</Label>
                      <p className="text-sm text-muted-foreground">
                        Notify when API errors occur
                      </p>
                    </div>
                    <Switch defaultChecked />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label>System Maintenance</Label>
                      <p className="text-sm text-muted-foreground">
                        Notify about scheduled maintenance
                      </p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security */}
        <TabsContent value="security" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Security Settings
              </CardTitle>
              <CardDescription>
                Configure authentication and security preferences
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="p-4 border border-yellow-200 bg-yellow-50 rounded">
                  <div className="flex items-center space-x-2">
                    <AlertTriangle className="h-5 w-5 text-yellow-600" />
                    <p className="text-sm font-medium text-yellow-800">
                      Security Configuration
                    </p>
                  </div>
                  <p className="text-sm text-yellow-700 mt-1">
                    Authentication and authorization settings will be configured once the backend authentication system is implemented.
                  </p>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 border rounded">
                    <div>
                      <p className="font-medium">API Authentication</p>
                      <p className="text-sm text-muted-foreground">JWT token-based authentication</p>
                    </div>
                    <Badge variant="secondary">Pending</Badge>
                  </div>

                  <div className="flex items-center justify-between p-3 border rounded">
                    <div>
                      <p className="font-medium">Role-based Access Control</p>
                      <p className="text-sm text-muted-foreground">RBAC for data access permissions</p>
                    </div>
                    <Badge variant="secondary">Pending</Badge>
                  </div>

                  <div className="flex items-center justify-between p-3 border rounded">
                    <div>
                      <p className="font-medium">Audit Logging</p>
                      <p className="text-sm text-muted-foreground">Track all data access and modifications</p>
                    </div>
                    <Badge variant="default">Active</Badge>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Appearance */}
        <TabsContent value="appearance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="h-5 w-5" />
                Appearance Settings
              </CardTitle>
              <CardDescription>
                Customize the look and feel of the dashboard
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Dark Mode</Label>
                  <p className="text-sm text-muted-foreground">
                    Switch to dark theme for better viewing in low light
                  </p>
                </div>
                <Switch checked={darkMode} onCheckedChange={setDarkMode} />
              </div>

              <Separator />

              <div className="space-y-4">
                <h4 className="font-medium">Chart Display Options</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Animated Charts</Label>
                      <p className="text-sm text-muted-foreground">
                        Enable smooth transitions and animations
                      </p>
                    </div>
                    <Switch defaultChecked />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label>High Contrast Mode</Label>
                      <p className="text-sm text-muted-foreground">
                        Increase contrast for better accessibility
                      </p>
                    </div>
                    <Switch />
                  </div>
                </div>
              </div>

              <Separator />

              <div className="space-y-2">
                <Label>Default Chart Type</Label>
                <Select defaultValue="bar">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="bar">Bar Chart</SelectItem>
                    <SelectItem value="line">Line Chart</SelectItem>
                    <SelectItem value="pie">Pie Chart</SelectItem>
                    <SelectItem value="area">Area Chart</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
      </div>
    </BudgetLayout>
  );
}
