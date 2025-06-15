import { useMutation } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { api } from '@/lib/api';
import { cacheInvalidator } from '@/components/providers/query-provider';
import type { Task, Project, Field, TaskFormData, ProjectFormData, FieldFormData } from '@/types';

/**
 * Custom mutation hooks with intelligent cache invalidation
 * 
 * These hooks provide optimistic updates and automatic cache invalidation
 * to keep the UI in sync with backend changes while maintaining performance.
 */

// Task Mutations
export const useTaskMutations = () => {
  const createTask = useMutation({
    mutationFn: (data: TaskFormData) => api.tasks.create(data),
    onSuccess: (newTask: Task) => {
      toast.success(`Task "${newTask.task_name}" created successfully`);
      cacheInvalidator.invalidateTaskRelated(newTask.id, 'background');
    },
    onError: (error) => {
      toast.error('Failed to create task');
      console.error('Create task error:', error);
    },
  });

  const updateTask = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<TaskFormData> }) => 
      api.tasks.update(id, data),
    onSuccess: (updatedTask: Task) => {
      toast.success(`Task "${updatedTask.task_name}" updated successfully`);
      cacheInvalidator.invalidateTaskRelated(updatedTask.id, 'background');
    },
    onError: (error) => {
      toast.error('Failed to update task');
      console.error('Update task error:', error);
    },
  });

  const deleteTask = useMutation({
    mutationFn: (id: number) => api.tasks.delete(id),
    onSuccess: (_, taskId) => {
      toast.success('Task deleted successfully');
      cacheInvalidator.invalidateTaskRelated(taskId, 'immediate');
    },
    onError: (error) => {
      toast.error('Failed to delete task');
      console.error('Delete task error:', error);
    },
  });

  const completeTask = useMutation({
    mutationFn: (id: number) => api.tasks.complete(id),
    onMutate: (taskId) => {
      // Optimistic update
      cacheInvalidator.optimisticCompleteTask(taskId, true);
    },
    onSuccess: (completedTask: Task) => {
      toast.success(`Task "${completedTask.task_name}" completed!`);
      cacheInvalidator.invalidateTaskRelated(completedTask.id, 'background');
    },
    onError: (error, taskId) => {
      // Rollback optimistic update
      cacheInvalidator.optimisticCompleteTask(taskId, false);
      toast.error('Failed to complete task');
      console.error('Complete task error:', error);
    },
  });

  const reopenTask = useMutation({
    mutationFn: (id: number) => api.tasks.reopen(id),
    onMutate: (taskId) => {
      // Optimistic update
      cacheInvalidator.optimisticCompleteTask(taskId, false);
    },
    onSuccess: (reopenedTask: Task) => {
      toast.success(`Task "${reopenedTask.task_name}" reopened`);
      cacheInvalidator.invalidateTaskRelated(reopenedTask.id, 'background');
    },
    onError: (error, taskId) => {
      // Rollback optimistic update
      cacheInvalidator.optimisticCompleteTask(taskId, true);
      toast.error('Failed to reopen task');
      console.error('Reopen task error:', error);
    },
  });

  const bulkCompleteTask = useMutation({
    mutationFn: (taskIds: number[]) => api.tasks.bulkComplete(taskIds),
    onSuccess: (_, taskIds) => {
      toast.success(`${taskIds.length} tasks completed!`);
      cacheInvalidator.invalidateTaskRelated(undefined, 'immediate');
    },
    onError: (error) => {
      toast.error('Failed to complete tasks');
      console.error('Bulk complete tasks error:', error);
    },
  });

  return {
    createTask,
    updateTask,
    deleteTask,
    completeTask,
    reopenTask,
    bulkCompleteTask,
  };
};

// Project Mutations
export const useProjectMutations = () => {
  const createProject = useMutation({
    mutationFn: (data: ProjectFormData) => api.projects.create(data),
    onSuccess: (newProject: Project) => {
      toast.success(`Project "${newProject.project_name}" created successfully`);
      cacheInvalidator.invalidateProjectRelated(newProject.id, 'background');
    },
    onError: (error) => {
      toast.error('Failed to create project');
      console.error('Create project error:', error);
    },
  });

  const updateProject = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<ProjectFormData> }) => 
      api.projects.update(id, data),
    onSuccess: (updatedProject: Project) => {
      toast.success(`Project "${updatedProject.project_name}" updated successfully`);
      cacheInvalidator.invalidateProjectRelated(updatedProject.id, 'background');
    },
    onError: (error) => {
      toast.error('Failed to update project');
      console.error('Update project error:', error);
    },
  });

  const deleteProject = useMutation({
    mutationFn: (id: number) => api.projects.delete(id),
    onSuccess: (_, projectId) => {
      toast.success('Project deleted successfully');
      cacheInvalidator.invalidateProjectRelated(projectId, 'immediate');
    },
    onError: (error) => {
      toast.error('Failed to delete project');
      console.error('Delete project error:', error);
    },
  });

  const completeProject = useMutation({
    mutationFn: (id: number) => api.projects.complete(id),
    onMutate: (projectId) => {
      // Optimistic update
      cacheInvalidator.optimisticCompleteProject(projectId, true);
    },
    onSuccess: (completedProject: Project) => {
      toast.success(`Project "${completedProject.project_name}" completed!`);
      cacheInvalidator.invalidateProjectRelated(completedProject.id, 'background');
    },
    onError: (error, projectId) => {
      // Rollback optimistic update
      cacheInvalidator.optimisticCompleteProject(projectId, false);
      toast.error('Failed to complete project');
      console.error('Complete project error:', error);
    },
  });

  return {
    createProject,
    updateProject,
    deleteProject,
    completeProject,
  };
};

// Field Mutations
export const useFieldMutations = () => {
  const createField = useMutation({
    mutationFn: (data: FieldFormData) => api.fields.create(data),
    onSuccess: (newField: Field) => {
      toast.success(`Field "${(newField as any).field_name || newField.name || newField.id}" created successfully`);
      cacheInvalidator.invalidateFieldRelated(newField.id, 'background');
    },
    onError: (error) => {
      toast.error('Failed to create field');
      console.error('Create field error:', error);
    },
  });

  const updateField = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<FieldFormData> }) => 
      api.fields.update(id, data),
    onSuccess: (updatedField: Field) => {
      toast.success(`Field "${(updatedField as any).field_name || updatedField.name || updatedField.id}" updated successfully`);
      cacheInvalidator.invalidateFieldRelated(updatedField.id, 'immediate'); // Fields need immediate refresh
    },
    onError: (error) => {
      toast.error('Failed to update field');
      console.error('Update field error:', error);
    },
  });

  const deleteField = useMutation({
    mutationFn: (id: number) => api.fields.delete(id),
    onSuccess: (_, fieldId) => {
      toast.success('Field deleted successfully');
      cacheInvalidator.invalidateFieldRelated(fieldId, 'immediate'); // Fields need immediate refresh
    },
    onError: (error) => {
      toast.error('Failed to delete field');
      console.error('Delete field error:', error);
    },
  });

  return {
    createField,
    updateField,
    deleteField,
  };
};

// User Settings Mutations (Device-specific)
export const useUserSettingsMutations = () => {
  const updateSetting = useMutation({
    mutationFn: ({ device, key, value }: { device: 'desktop' | 'tablet' | 'phone'; key: string; value: any }) => 
      api.userSettings.update(device, key, value),
    onSuccess: (_, { key }) => {
      cacheInvalidator.invalidateUserSettings(key, 'immediate');
    },
    onError: (error) => {
      toast.error('Failed to save settings');
      console.error('Update setting error:', error);
    },
  });

  const updateDeviceSettings = useMutation({
    mutationFn: ({ device, settings }: { device: 'desktop' | 'tablet' | 'phone'; settings: Record<string, any> }) => 
      api.userSettings.updateDevice(device, settings),
    onSuccess: () => {
      toast.success('Settings saved successfully');
      cacheInvalidator.invalidateUserSettings(undefined, 'immediate');
    },
    onError: (error) => {
      toast.error('Failed to save settings');
      console.error('Update device settings error:', error);
    },
  });

  const deleteSetting = useMutation({
    mutationFn: ({ device, key }: { device: 'desktop' | 'tablet' | 'phone'; key: string }) => 
      api.userSettings.delete(device, key),
    onSuccess: (_, { key }) => {
      toast.success('Setting reset to default');
      cacheInvalidator.invalidateUserSettings(key, 'immediate');
    },
    onError: (error) => {
      toast.error('Failed to reset setting');
      console.error('Delete setting error:', error);
    },
  });

  const resetAllSettings = useMutation({
    mutationFn: () => api.userSettings.reset(),
    onSuccess: () => {
      toast.success('All settings reset to defaults');
      cacheInvalidator.invalidateUserSettings(undefined, 'immediate');
    },
    onError: (error) => {
      toast.error('Failed to reset settings');
      console.error('Reset settings error:', error);
    },
  });

  return {
    updateSetting,
    updateDeviceSettings,
    deleteSetting,
    resetAllSettings,
  };
};