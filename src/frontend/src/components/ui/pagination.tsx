'use client';

import * as React from 'react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface PaginationProps {
  currentPage: number;
  totalItems: number;
  itemsPerPage: number;
  onPageChange: (page: number) => void;
  onShowAll: () => void;
  isShowingAll: boolean;
  className?: string;
}

export function Pagination({
  currentPage,
  totalItems,
  itemsPerPage,
  onPageChange,
  onShowAll,
  isShowingAll,
  className
}: PaginationProps) {
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  
  // Don't render if there's only one page or less
  if (totalItems <= itemsPerPage && !isShowingAll) {
    return null;
  }

  // Generate page numbers to display
  const getPageNumbers = () => {
    const pages: number[] = [];
    const maxVisiblePages = 10;
    
    if (totalPages <= maxVisiblePages) {
      // Show all pages if total is small
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Show first few, current area, and last few
      const start = Math.max(1, currentPage - 2);
      const end = Math.min(totalPages, currentPage + 2);
      
      // Always include first page
      if (start > 1) {
        pages.push(1);
        if (start > 2) {
          pages.push(-1); // Ellipsis marker
        }
      }
      
      // Add current area
      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
      
      // Always include last page
      if (end < totalPages) {
        if (end < totalPages - 1) {
          pages.push(-2); // Ellipsis marker
        }
        pages.push(totalPages);
      }
    }
    
    return pages;
  };

  const pageNumbers = getPageNumbers();

  return (
    <div className={cn("flex items-center justify-center space-x-2", className)}>
      {/* Page Number Buttons */}
      <div className="flex items-center space-x-1">
        {pageNumbers.map((pageNum, index) => {
          if (pageNum === -1 || pageNum === -2) {
            // Ellipsis
            return (
              <span key={`ellipsis-${index}`} className="px-2 py-1 text-muted-foreground">
                ...
              </span>
            );
          }
          
          const isActive = pageNum === currentPage && !isShowingAll;
          
          return (
            <Button
              key={pageNum}
              variant={isActive ? "default" : "outline"}
              size="sm"
              onClick={() => onPageChange(pageNum)}
              className={cn(
                "min-w-[2.5rem] h-9",
                isActive && "bg-primary text-primary-foreground"
              )}
            >
              {pageNum}
            </Button>
          );
        })}
      </div>

      {/* Show All Button */}
      <div className="ml-4 pl-4 border-l border-border">
        <Button
          variant={isShowingAll ? "default" : "outline"}
          size="sm"
          onClick={onShowAll}
          className={cn(
            "min-w-[4rem]",
            isShowingAll && "bg-primary text-primary-foreground"
          )}
        >
          Show All
        </Button>
      </div>

      {/* Info Text */}
      <div className="ml-4 text-sm text-muted-foreground">
        {isShowingAll 
          ? `Showing all ${totalItems} items`
          : `Page ${currentPage} of ${totalPages} (${totalItems} total)`
        }
      </div>
    </div>
  );
}

// Hook for pagination state management
export function usePagination(totalItems: number, initialItemsPerPage: number = 50) {
  const [currentPage, setCurrentPage] = React.useState(1);
  const [itemsPerPage] = React.useState(initialItemsPerPage);
  const [isShowingAll, setIsShowingAll] = React.useState(false);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    setIsShowingAll(false);
  };

  const handleShowAll = () => {
    setIsShowingAll(true);
    setCurrentPage(1);
  };

  const resetPagination = () => {
    setCurrentPage(1);
    setIsShowingAll(false);
  };

  // Calculate offset for API calls
  const offset = isShowingAll ? 0 : (currentPage - 1) * itemsPerPage;
  const limit = isShowingAll ? totalItems : itemsPerPage;

  return {
    currentPage,
    itemsPerPage,
    isShowingAll,
    offset,
    limit,
    handlePageChange,
    handleShowAll,
    resetPagination,
  };
}