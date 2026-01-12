import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Upload, 
  FileText, 
  Trash2, 
  RefreshCw, 
  CheckCircle2, 
  XCircle, 
  Clock,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { getApiUrl, API_ENDPOINTS } from '@/config/api';
import { toast } from '@/hooks/use-toast';
import {
  PDFMetadata,
  PDFListResponse,
  GeminiFilesResponse,
  PDFSyncResponse,
  PDFUploadResponse,
  PDFDeleteResponse,
  PDFCategory,
  PDF_CATEGORIES,
  GeminiFileInfo
} from '@/types/pdf';

export const PDFManager: React.FC = () => {
  const [pdfs, setPdfs] = useState<PDFMetadata[]>([]);
  const [geminiFiles, setGeminiFiles] = useState<GeminiFileInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<PDFCategory | 'all'>('all');
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadCategory, setUploadCategory] = useState<PDFCategory>('research_papers');
  const [isUploading, setIsUploading] = useState(false);

  // Load PDFs on mount and when category changes
  useEffect(() => {
    loadPDFs();
    loadGeminiFiles();
  }, [selectedCategory]);

  const loadPDFs = async () => {
    setIsLoading(true);
    try {
      const categoryParam = selectedCategory !== 'all' ? `?category=${selectedCategory}` : '';
      const response = await fetch(getApiUrl(API_ENDPOINTS.pdfs.list + categoryParam));
      
      if (!response.ok) {
        throw new Error('Failed to load PDFs');
      }
      
      const data: PDFListResponse = await response.json();
      setPdfs(data.pdfs);
    } catch (error) {
      console.error('Error loading PDFs:', error);
      toast({
        title: 'Error',
        description: 'Failed to load PDF list',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const loadGeminiFiles = async () => {
    try {
      const response = await fetch(getApiUrl(API_ENDPOINTS.pdfs.geminiFiles));
      
      if (!response.ok) {
        throw new Error('Failed to load Gemini files');
      }
      
      const data: GeminiFilesResponse = await response.json();
      setGeminiFiles(data.files);
    } catch (error) {
      console.error('Error loading Gemini files:', error);
    }
  };

  const handleUpload = async () => {
    if (!uploadFile) return;

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('category', uploadCategory);

      const response = await fetch(getApiUrl(API_ENDPOINTS.pdfs.upload), {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Upload failed');
      }

      const data: PDFUploadResponse = await response.json();
      
      toast({
        title: 'Success',
        description: data.message,
      });

      // Reset form and reload
      setUploadFile(null);
      await loadPDFs();
      await loadGeminiFiles();
    } catch (error) {
      console.error('Error uploading PDF:', error);
      toast({
        title: 'Upload Failed',
        description: error instanceof Error ? error.message : 'Failed to upload PDF',
        variant: 'destructive',
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleSync = async () => {
    setIsSyncing(true);
    try {
      const categoryParam = selectedCategory !== 'all' ? `?category=${selectedCategory}` : '';
      const response = await fetch(
        getApiUrl(API_ENDPOINTS.pdfs.sync + categoryParam),
        { method: 'POST' }
      );

      if (!response.ok) {
        throw new Error('Sync failed');
      }

      const data: PDFSyncResponse = await response.json();
      
      toast({
        title: 'Sync Complete',
        description: data.message,
      });

      await loadGeminiFiles();
    } catch (error) {
      console.error('Error syncing PDFs:', error);
      toast({
        title: 'Sync Failed',
        description: 'Failed to sync PDFs to Gemini',
        variant: 'destructive',
      });
    } finally {
      setIsSyncing(false);
    }
  };

  const handleDelete = async (fileName: string) => {
    if (!confirm(`Are you sure you want to delete "${fileName}"?`)) {
      return;
    }

    try {
      const response = await fetch(
        getApiUrl(API_ENDPOINTS.pdfs.delete(fileName)),
        { method: 'DELETE' }
      );

      if (!response.ok) {
        throw new Error('Delete failed');
      }

      const data: PDFDeleteResponse = await response.json();
      
      toast({
        title: 'Success',
        description: data.message,
      });

      await loadPDFs();
      await loadGeminiFiles();
    } catch (error) {
      console.error('Error deleting PDF:', error);
      toast({
        title: 'Delete Failed',
        description: 'Failed to delete PDF',
        variant: 'destructive',
      });
    }
  };

  const getGeminiStatus = (displayName: string): GeminiFileInfo | undefined => {
    return geminiFiles.find(f => f.display_name === displayName);
  };

  const getStatusBadge = (status?: GeminiFileInfo) => {
    if (!status) {
      return <Badge variant="outline" className="text-xs">Not Synced</Badge>;
    }

    switch (status.state) {
      case 'ACTIVE':
        return (
          <Badge variant="default" className="text-xs bg-green-500">
            <CheckCircle2 className="h-3 w-3 mr-1" />
            Active
          </Badge>
        );
      case 'PROCESSING':
        return (
          <Badge variant="secondary" className="text-xs">
            <Clock className="h-3 w-3 mr-1" />
            Processing
          </Badge>
        );
      case 'FAILED':
        return (
          <Badge variant="destructive" className="text-xs">
            <XCircle className="h-3 w-3 mr-1" />
            Failed
          </Badge>
        );
      default:
        return <Badge variant="outline" className="text-xs">Unknown</Badge>;
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const groupedPDFs = pdfs.reduce((acc, pdf) => {
    if (!acc[pdf.category]) {
      acc[pdf.category] = [];
    }
    acc[pdf.category].push(pdf);
    return acc;
  }, {} as Record<string, PDFMetadata[]>);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Document Library
          </CardTitle>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleSync}
              disabled={isSyncing}
            >
              {isSyncing ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <RefreshCw className="h-4 w-4" />
              )}
              <span className="ml-2">Sync to Gemini</span>
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Info Banner */}
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Upload PDFs to enable AI-powered document search. The chat will automatically search these documents when relevant.
          </AlertDescription>
        </Alert>

        {/* Upload Section */}
        <div className="border rounded-lg p-4 space-y-3">
          <h3 className="font-semibold text-sm">Upload New Document</h3>
          <div className="flex gap-2">
            <Input
              type="file"
              accept=".pdf"
              onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
              disabled={isUploading}
              className="flex-1"
            />
            <Select
              value={uploadCategory}
              onValueChange={(value) => setUploadCategory(value as PDFCategory)}
              disabled={isUploading}
            >
              <SelectTrigger className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {PDF_CATEGORIES.map((cat) => (
                  <SelectItem key={cat.value} value={cat.value}>
                    {cat.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button
              onClick={handleUpload}
              disabled={!uploadFile || isUploading}
            >
              {isUploading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Upload className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>

        {/* Filter */}
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">Filter:</span>
          <Select
            value={selectedCategory}
            onValueChange={(value) => setSelectedCategory(value as PDFCategory | 'all')}
          >
            <SelectTrigger className="w-[200px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Categories</SelectItem>
              {PDF_CATEGORIES.map((cat) => (
                <SelectItem key={cat.value} value={cat.value}>
                  {cat.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* PDF List */}
        <ScrollArea className="h-[400px] border rounded-lg">
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : pdfs.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-muted-foreground p-8 text-center">
              <FileText className="h-12 w-12 mb-2 opacity-50" />
              <p className="text-sm">No documents uploaded yet</p>
              <p className="text-xs mt-1">Upload a PDF to get started</p>
            </div>
          ) : (
            <div className="p-4 space-y-4">
              {Object.entries(groupedPDFs).map(([category, categoryPdfs]) => (
                <div key={category} className="space-y-2">
                  <h4 className="font-semibold text-sm text-muted-foreground uppercase">
                    {PDF_CATEGORIES.find(c => c.value === category)?.label || category}
                  </h4>
                  <div className="space-y-2">
                    {categoryPdfs.map((pdf) => {
                      const geminiStatus = getGeminiStatus(pdf.display_name);
                      return (
                        <div
                          key={pdf.hash}
                          className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors"
                        >
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <FileText className="h-4 w-4 flex-shrink-0 text-blue-500" />
                              <span className="font-medium text-sm truncate">
                                {pdf.display_name}
                              </span>
                            </div>
                            <div className="flex items-center gap-2 mt-1">
                              <span className="text-xs text-muted-foreground">
                                {formatFileSize(pdf.size_bytes)}
                              </span>
                              {getStatusBadge(geminiStatus)}
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(pdf.name)}
                            className="ml-2"
                          >
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>

        {/* Summary */}
        <div className="flex items-center justify-between text-xs text-muted-foreground pt-2 border-t">
          <span>{pdfs.length} document{pdfs.length !== 1 ? 's' : ''} total</span>
          <span>{geminiFiles.filter(f => f.state === 'ACTIVE').length} active in Gemini</span>
        </div>
      </CardContent>
    </Card>
  );
};