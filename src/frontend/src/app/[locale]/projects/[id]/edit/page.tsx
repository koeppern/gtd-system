'use client';

import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { useTranslations } from 'next-intl';
import { ProjectEditForm } from '@/components/projects/project-edit-form';
import { BackButton } from '@/components/ui/back-button';
import { api } from '@/lib/api';

export default function ProjectEditPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const t = useTranslations('projects');
  const tCommon = useTranslations('common');
  
  const projectId = parseInt(params.id as string);
  const returnTo = searchParams.get('returnTo') || '/projects';

  // Fetch project data
  const { data: project, isLoading, error } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => api.projects.getById(projectId),
    enabled: !isNaN(projectId),
  });

  const handleBack = () => {
    // Navigate back with highlight parameter
    const url = new URL(returnTo, window.location.origin);
    url.searchParams.set('highlight', projectId.toString());
    router.push(url.pathname + url.search);
  };

  const handleSaveSuccess = () => {
    // After successful save, navigate back with highlight
    handleBack();
  };

  if (isNaN(projectId)) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <h2 className="text-lg font-semibold text-foreground mb-2">
            Invalid Project ID
          </h2>
          <p className="text-muted-foreground mb-4">
            The project ID provided is not valid.
          </p>
          <BackButton onClick={handleBack} />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <h2 className="text-lg font-semibold text-foreground mb-2">
            {tCommon('common.error')}
          </h2>
          <p className="text-muted-foreground mb-4">
            Failed to load project data.
          </p>
          <BackButton onClick={handleBack} />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Back Button */}
      <div className="flex items-center space-x-4">
        <BackButton onClick={handleBack} />
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            {isLoading ? tCommon('common.loading') : `Edit: ${project?.project_name || project?.name}`}
          </h1>
          <p className="text-muted-foreground">
            Modify project details and settings
          </p>
        </div>
      </div>

      {/* Edit Form */}
      {isLoading ? (
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
            <p className="mt-2 text-muted-foreground">{tCommon('common.loading')}</p>
          </div>
        </div>
      ) : project ? (
        <ProjectEditForm 
          project={project} 
          onSaveSuccess={handleSaveSuccess}
          onCancel={handleBack}
        />
      ) : null}
    </div>
  );
}