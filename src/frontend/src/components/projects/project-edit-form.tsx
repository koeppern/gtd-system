'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useTranslations } from 'next-intl';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { api } from '@/lib/api';

interface Project {
  id: number;
  project_name?: string;
  name?: string;
  readings?: string;
  field_id?: number;
  keywords?: string;
  mother_project?: string;
  related_projects?: string;
  gtd_processes?: string;
  do_this_week?: boolean;
  done_at?: string;
  // Add other project fields as needed
}

interface ProjectEditFormProps {
  project: Project;
  onSaveSuccess: () => void;
  onCancel: () => void;
}

export function ProjectEditForm({ project, onSaveSuccess, onCancel }: ProjectEditFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const t = useTranslations('projects');
  const tCommon = useTranslations('common');

  const form = useForm({
    defaultValues: {
      project_name: project.project_name || project.name || '',
      readings: project.readings || '',
      keywords: project.keywords || '',
      mother_project: project.mother_project || '',
      related_projects: project.related_projects || '',
      gtd_processes: project.gtd_processes || '',
      do_this_week: project.do_this_week || false,
    }
  });

  const onSubmit = async (data: any) => {
    setIsLoading(true);
    try {
      await api.projects.update(project.id, data);
      onSaveSuccess();
    } catch (error) {
      console.error('Failed to update project:', error);
      // TODO: Add proper error handling
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Edit Project</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            {/* Project Name */}
            <div className="space-y-2">
              <Label htmlFor="project_name">{t('table.projectName')}</Label>
              <Input
                id="project_name"
                {...form.register('project_name', { required: true })}
                placeholder={t('placeholders.projectName')}
              />
            </div>

            {/* Keywords */}
            <div className="space-y-2">
              <Label htmlFor="keywords">{tCommon('table.keywords')}</Label>
              <Input
                id="keywords"
                {...form.register('keywords')}
                placeholder="Enter keywords..."
              />
            </div>

            {/* Readings */}
            <div className="space-y-2">
              <Label htmlFor="readings">{tCommon('table.readings')}</Label>
              <Textarea
                id="readings"
                {...form.register('readings')}
                placeholder="Enter readings..."
                rows={3}
              />
            </div>

            {/* Mother Project */}
            <div className="space-y-2">
              <Label htmlFor="mother_project">{tCommon('table.parentProject')}</Label>
              <Input
                id="mother_project"
                {...form.register('mother_project')}
                placeholder="Enter parent project..."
              />
            </div>

            {/* Related Projects */}
            <div className="space-y-2">
              <Label htmlFor="related_projects">Related Projects</Label>
              <Textarea
                id="related_projects"
                {...form.register('related_projects')}
                placeholder="Enter related projects..."
                rows={2}
              />
            </div>

            {/* GTD Processes */}
            <div className="space-y-2">
              <Label htmlFor="gtd_processes">{tCommon('table.gtdProcesses')}</Label>
              <Textarea
                id="gtd_processes"
                {...form.register('gtd_processes')}
                placeholder="Enter GTD processes..."
                rows={2}
              />
            </div>

            {/* Do This Week */}
            <div className="flex items-center space-x-2">
              <Checkbox
                id="do_this_week"
                {...form.register('do_this_week')}
              />
              <Label htmlFor="do_this_week">{tCommon('status.thisWeek')}</Label>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-end space-x-4 pt-6">
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isLoading}
              >
                {isLoading ? tCommon('common.loading') : 'Save Changes'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}