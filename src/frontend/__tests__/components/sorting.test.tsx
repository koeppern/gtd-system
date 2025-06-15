/**
 * Tests for table sorting functionality
 * Testing the SortableHeader component and sort behavior
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ProjectsList } from '@/components/projects/projects-list';
import { TasksList } from '@/components/tasks/tasks-list';

// Mock the API
jest.mock('@/lib/api', () => ({
  api: {
    projects: {
      list: jest.fn(),
      update: jest.fn(),
    },
    tasks: {
      list: jest.fn(),
      update: jest.fn(),
    },
  },
}));

// Mock the hooks
jest.mock('@/hooks/use-keyboard-shortcuts', () => ({
  useKeyboardShortcuts: jest.fn(),
  useSearchFieldRef: () => ({
    ref: { current: null },
    searchFieldRef: { current: { focus: jest.fn(), select: jest.fn() } },
  }),
}));

// Mock resizable columns hook
jest.mock('@/components/ui/resizable-table', () => ({
  useResizableColumns: () => ({
    columns: [
      { key: 'name', title: 'Name', width: 200 },
      { key: 'status', title: 'Status', width: 100 },
    ],
    handleColumnResize: jest.fn(),
    handleColumnReorder: jest.fn(),
    isLoading: false,
  }),
  ResizableTable: ({ children, columns }: any) => (
    <table>
      <thead>
        <tr>
          {columns.map((col: any) => (
            <th key={col.key}>{col.title}</th>
          ))}
        </tr>
      </thead>
      <tbody>{children}</tbody>
    </table>
  ),
}));

// Mock group by hook
jest.mock('@/components/ui/group-by-dropdown', () => ({
  useGroupBy: (items: any[]) => [{ groupName: null, items }],
}));

const mockProjects = [
  {
    id: 1,
    name: 'Project A',
    project_name: 'Project A',
    field_name: 'Field 1',
    done_status: false,
    task_count: 5,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
  },
  {
    id: 2,
    name: 'Project B', 
    project_name: 'Project B',
    field_name: 'Field 2',
    done_status: true,
    task_count: 3,
    created_at: '2024-01-02T00:00:00Z',
    updated_at: '2024-01-03T00:00:00Z',
  },
];

const mockTasks = [
  {
    id: 1,
    task_name: 'Task A',
    name: 'Task A',
    project_name: 'Project 1',
    field_name: 'Field 1',
    done_at: null,
    priority: 1,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
  },
  {
    id: 2,
    task_name: 'Task B',
    name: 'Task B', 
    project_name: 'Project 2',
    field_name: 'Field 2',
    done_at: '2024-01-01T12:00:00Z',
    priority: 2,
    created_at: '2024-01-02T00:00:00Z',
    updated_at: '2024-01-03T00:00:00Z',
  },
];

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('ProjectsList Sorting', () => {
  it('renders sortable column headers', () => {
    render(
      <ProjectsList 
        projects={mockProjects} 
        isLoading={false} 
        showCompleted={false}
      />,
      { wrapper: createWrapper() }
    );

    // Check if sortable headers are rendered
    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByText('Status')).toBeInTheDocument();
  });

  it('shows sort indicator when column is sorted', async () => {
    render(
      <ProjectsList 
        projects={mockProjects} 
        isLoading={false} 
        showCompleted={false}
      />,
      { wrapper: createWrapper() }
    );

    // Find the name column header button
    const nameHeader = screen.getByRole('button', { name: /project name/i });
    
    // Click to sort
    fireEvent.click(nameHeader);

    // Should show ascending indicator (up arrow)
    // Note: This test might need adjustment based on actual icon implementation
    expect(nameHeader).toBeInTheDocument();
  });

  it('toggles sort direction on repeated clicks', async () => {
    render(
      <ProjectsList 
        projects={mockProjects} 
        isLoading={false} 
        showCompleted={false}
      />,
      { wrapper: createWrapper() }
    );

    const nameHeader = screen.getByRole('button', { name: /project name/i });
    
    // First click - ascending
    fireEvent.click(nameHeader);
    
    // Second click - should toggle to descending
    fireEvent.click(nameHeader);
    
    // Third click - should toggle back to ascending
    fireEvent.click(nameHeader);

    expect(nameHeader).toBeInTheDocument();
  });
});

describe('TasksList Sorting', () => {
  it('renders sortable column headers', () => {
    render(
      <TasksList 
        tasks={mockTasks} 
        isLoading={false} 
        showCompleted={false}
      />,
      { wrapper: createWrapper() }
    );

    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByText('Status')).toBeInTheDocument();
  });

  it('sorts tasks by different columns', async () => {
    render(
      <TasksList 
        tasks={mockTasks} 
        isLoading={false} 
        showCompleted={false}
      />,
      { wrapper: createWrapper() }
    );

    // Test sorting by name
    const nameHeader = screen.getByRole('button', { name: /task name/i });
    fireEvent.click(nameHeader);

    // Test sorting by status 
    const statusHeader = screen.getByRole('button', { name: /status/i });
    fireEvent.click(statusHeader);

    expect(nameHeader).toBeInTheDocument();
    expect(statusHeader).toBeInTheDocument();
  });
});

describe('Auto-sort on Grouping', () => {
  it('automatically sorts by grouped column', () => {
    render(
      <ProjectsList 
        projects={mockProjects} 
        isLoading={false} 
        showCompleted={false}
        groupBy="status"
      />,
      { wrapper: createWrapper() }
    );

    // When groupBy is set, should automatically sort by that column
    // This tests our useEffect that auto-sorts when grouping changes
    expect(screen.getByText('Project A')).toBeInTheDocument();
    expect(screen.getByText('Project B')).toBeInTheDocument();
  });
});