// Core GTD Types matching the backend schema

export interface User {
  id: string;
  first_name?: string;
  last_name?: string;
  email_address: string;
  timezone: string;
  date_format: string;
  time_format: string;
  weekly_review_day: number;
  is_active: boolean;
  email_verified: boolean;
  last_login_at?: string;
  created_at: string;
  updated_at: string;
  deleted_at?: string;
  full_name: string;
  display_name: string;
}

export interface Field {
  id: number;
  name: string;
  description?: string;
  color?: string;
  icon?: string;
  created_at: string;
  updated_at: string;
  deleted_at?: string;
  project_count: number;
  task_count: number;
}

export interface Project {
  id: number;
  user_id: string;
  project_name: string;
  readings?: string;
  field_id?: number;
  keywords?: string;
  mother_project?: string;
  related_projects?: string;
  related_mother_projects?: string;
  related_knowledge_vault?: string;
  related_tasks?: string;
  do_this_week: boolean;
  gtd_processes?: string;
  add_checkboxes?: string;
  done_at?: string;
  notion_export_row?: number;
  source_file?: string;
  created_at: string;
  updated_at: string;
  deleted_at?: string;
  is_done: boolean;
  is_active: boolean;
  field?: Field;
  task_count: number;
  completed_task_count: number;
  completion_percentage: number;
}

export interface Task {
  id: number;
  user_id: string;
  task_name: string;
  task_notes?: string;
  field_id?: number;
  project_id?: number;
  priority?: number;
  do_today: boolean;
  do_this_week: boolean;
  do_on_date?: string;
  is_reading: boolean;
  wait_for: boolean;
  postponed: boolean;
  done_at?: string;
  notion_export_row?: number;
  source_file?: string;
  created_at: string;
  updated_at: string;
  deleted_at?: string;
  is_done: boolean;
  is_active: boolean;
  field?: Field;
  project?: Project;
}

// API Response Types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface ApiError {
  success: boolean;
  error: {
    code: string;
    message: string;
    field?: string;
  };
  timestamp: string;
}

export interface ApiSuccess {
  success: boolean;
  message: string;
  timestamp: string;
}

// Dashboard Types
export interface DashboardStats {
  total_projects: number;
  active_projects: number;
  completed_projects: number;
  total_tasks: number;
  pending_tasks: number;
  completed_tasks: number;
  tasks_today: number;
  tasks_this_week: number;
  overdue_tasks: number;
  completion_rate_7d: number;
  completion_rate_30d: number;
}

export interface QuickAddRequest {
  content: string;
  type?: 'task' | 'project';
  field?: string;
  project_name?: string;
  priority?: number;
  do_today?: boolean;
  do_this_week?: boolean;
}

// UI State Types
export interface FilterState {
  field_id?: number;
  is_done?: boolean;
  do_this_week?: boolean;
  do_today?: boolean;
  priority?: number;
  search?: string;
}

export interface SortState {
  field: 'created_at' | 'updated_at' | 'priority' | 'task_name' | 'project_name';
  direction: 'asc' | 'desc';
}

export interface ViewState {
  layout: 'list' | 'grid' | 'kanban';
  groupBy?: 'field' | 'priority' | 'project' | 'status';
  showCompleted: boolean;
  compactMode: boolean;
}

// Form Types
export interface TaskFormData {
  task_name: string;
  task_notes?: string;
  field_id?: number;
  project_id?: number;
  priority?: number;
  do_today: boolean;
  do_this_week: boolean;
  do_on_date?: string;
  is_reading: boolean;
  wait_for: boolean;
  postponed: boolean;
}

export interface ProjectFormData {
  project_name: string;
  readings?: string;
  field_id?: number;
  keywords?: string;
  do_this_week: boolean;
}

export interface FieldFormData {
  name: string;
  description?: string;
  color?: string;
  icon?: string;
}

// Navigation Types
export interface NavItem {
  label: string;
  href: string;
  icon?: string;
  badge?: number;
  shortcut?: string;
}

export interface Breadcrumb {
  label: string;
  href?: string;
}

// Keyboard Shortcut Types
export interface KeyboardShortcut {
  key: string;
  description: string;
  action: () => void;
  category: 'navigation' | 'actions' | 'editing';
}

// Theme Types
export type Theme = 'light' | 'dark' | 'system';

// GTD Context Types
export type GTDContext = 
  | 'inbox'
  | 'today'
  | 'week'
  | 'projects'
  | 'waiting'
  | 'someday'
  | 'reference';

export interface GTDContextConfig {
  name: string;
  icon: string;
  description: string;
  color: string;
  filter: FilterState;
}

// Drag and Drop Types
export interface DragItem {
  id: string;
  type: 'task' | 'project';
  data: Task | Project;
}

export interface DropTarget {
  id: string;
  type: 'field' | 'project' | 'context';
  accepts: ('task' | 'project')[];
}

// Search Types
export interface SearchResult {
  id: number;
  type: 'project' | 'task';
  title: string;
  description?: string;
  field_name?: string;
  is_completed: boolean;
  completed_at?: string;
  relevance_score: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total_found: number;
  search_time_ms: number;
}

// Settings Types
export interface UserSettings {
  timezone: string;
  date_format: string;
  time_format: string;
  weekly_review_day: number;
  email_notifications: boolean;
  daily_digest: boolean;
  weekly_review_reminder: boolean;
  theme: Theme;
  compact_view: boolean;
  show_completed: boolean;
}

// Export utility types
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;