import { useState, FormEvent } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { Upload, FileText, AlertTriangle, DollarSign, CheckCircle, XCircle, Clock, Shield } from 'lucide-react';
import NovartisLogo from '@/components/NovartisLogo';

interface BidAnalysisResult {
  success: boolean;
  supplier: string;
  overall_score: number;
  weighted_scores: {
    technical: number;
    risk: number;
    financial: number;
  };
  technical_analysis: {
    supplier: string;
    extracted_specs: Record<string, any>;
    sop_parameters: Record<string, any>;
    deviations: Array<{
      parameter: string;
      value: number;
      sop_range: string;
      tolerance_range: string;
      deviation_pct: number;
    }>;
    compliance_score: number;
    status: string;
    raw_extraction?: string;
    error?: string;
  };
  risk_assessment: {
    supplier: string;
    financial_score: number;
    esg_score: number;
    overall_risk_score: number;
    red_flags: string[];
    status: string;
    recommendation: string;
  };
  financial_analysis: {
    supplier: string;
    bid_price: number;
    quantity: number;
    should_cost_breakdown: {
      material_cost: number;
      labor_cost: number;
      target_margin: string;
      total_should_cost: number;
    };
    variance: number;
    variance_threshold: string;
    status: string;
    recommendation: string;
  };
  executive_summary: string;
  final_recommendation: {
    decision: string;
    confidence: string;
    reason: string;
    requires_human_approval: boolean;
    next_steps: string[];
  };
  processing_time_seconds: number;
  timestamp: string;
  error?: string;
}

const IntelligenceHub = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [supplierName, setSupplierName] = useState('');
  const [bidPrice, setBidPrice] = useState('');
  const [quantity, setQuantity] = useState('');
  const [materialType, setMaterialType] = useState('api_base');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<BidAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    if (!selectedFile) {
      setError('Please select a bid PDF file');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('supplier_name', supplierName);
      formData.append('bid_price', bidPrice);
      formData.append('quantity', quantity);
      formData.append('material_type', materialType);

      const response = await fetch('http://localhost:8000/api/v1/procurement/analyze-bid', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to analyze bid');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err instanceof Error ? err.message : 'Failed to analyze bid. Please ensure the backend server is running.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { variant: 'default' | 'destructive' | 'outline' | 'secondary', label: string }> = {
      'PASS': { variant: 'default', label: 'Pass' },
      'FAIL': { variant: 'destructive', label: 'Fail' },
      'LOW_RISK': { variant: 'default', label: 'Low Risk' },
      'MEDIUM_RISK': { variant: 'secondary', label: 'Medium Risk' },
      'HIGH_RISK': { variant: 'destructive', label: 'High Risk' },
      'DISQUALIFIED': { variant: 'destructive', label: 'Disqualified' },
      'FAIR_PRICE': { variant: 'default', label: 'Fair Price' },
      'OVERPRICED': { variant: 'destructive', label: 'Overpriced' },
      'UNDERPRICED': { variant: 'secondary', label: 'Underpriced' },
      'RECOMMEND_AWARD': { variant: 'default', label: 'Recommend Award' },
      'CONDITIONAL_APPROVAL': { variant: 'secondary', label: 'Conditional' },
      'REQUEST_CLARIFICATION': { variant: 'outline', label: 'Needs Clarification' },
      'REJECT': { variant: 'destructive', label: 'Reject' }
    };

    const config = statusMap[status] || { variant: 'outline' as const, label: status };
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-start justify-between mb-4">
            <h1 className="text-4xl font-bold text-gray-900">🧠 Procurement Intelligence Hub</h1>
            <NovartisLogo className="h-12" />
          </div>
          <p className="text-lg text-gray-600 mb-4">Multi-Agent System for Pharmaceutical Bid Evaluation</p>
          <div className="flex gap-2">
            <Badge variant="outline" className="flex items-center gap-1">
              <Shield className="w-3 h-3" />
              GxP Compliant
            </Badge>
            <Badge variant="outline">21 CFR Part 11</Badge>
            <Badge variant="outline">Audit Trail Enabled</Badge>
          </div>
        </div>

        {/* Input Form */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Submit Bid for Analysis</CardTitle>
            <CardDescription>
              Upload a pharmaceutical bid PDF and provide supplier details for automated evaluation
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                {/* File Upload */}
                <div className="space-y-2">
                  <Label htmlFor="file">Bid PDF Document *</Label>
                  <div className="flex items-center gap-2">
                    <Input
                      id="file"
                      type="file"
                      accept=".pdf"
                      onChange={handleFileChange}
                      required
                      className="cursor-pointer"
                    />
                    {selectedFile && (
                      <FileText className="w-5 h-5 text-green-600" />
                    )}
                  </div>
                  {selectedFile && (
                    <p className="text-sm text-gray-600">Selected: {selectedFile.name}</p>
                  )}
                </div>

                {/* Supplier Name */}
                <div className="space-y-2">
                  <Label htmlFor="supplier">Supplier Name *</Label>
                  <Input
                    id="supplier"
                    value={supplierName}
                    onChange={(e) => setSupplierName(e.target.value)}
                    placeholder="e.g., Acme Pharma"
                    required
                  />
                </div>

                {/* Bid Price */}
                <div className="space-y-2">
                  <Label htmlFor="price">Bid Price (USD) *</Label>
                  <Input
                    id="price"
                    type="number"
                    step="0.01"
                    min="0"
                    value={bidPrice}
                    onChange={(e) => setBidPrice(e.target.value)}
                    placeholder="e.g., 150000"
                    required
                  />
                </div>

                {/* Quantity */}
                <div className="space-y-2">
                  <Label htmlFor="quantity">Quantity (Units) *</Label>
                  <Input
                    id="quantity"
                    type="number"
                    min="1"
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    placeholder="e.g., 1000"
                    required
                  />
                </div>

                {/* Material Type */}
                <div className="space-y-2">
                  <Label htmlFor="material">Material Type</Label>
                  <select
                    id="material"
                    value={materialType}
                    onChange={(e) => setMaterialType(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="api_base">API Base</option>
                    <option value="excipient">Excipient</option>
                    <option value="packaging">Packaging</option>
                  </select>
                </div>
              </div>

              {error && (
                <Alert variant="destructive">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <Button
                type="submit"
                disabled={isAnalyzing}
                className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
              >
                {isAnalyzing ? (
                  <>
                    <Clock className="w-4 h-4 mr-2 animate-spin" />
                    Analyzing Bid...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4 mr-2" />
                    Analyze Bid
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Results */}
        {result && (
          <div className="space-y-6">
            {/* Overall Score Card */}
            <Card className="border-2 border-blue-200">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-2xl">Analysis Results: {result.supplier}</CardTitle>
                    <CardDescription>
                      Processed in {result.processing_time_seconds}s | {new Date(result.timestamp).toLocaleString()}
                    </CardDescription>
                  </div>
                  <div className="text-right">
                    <div className={`text-4xl font-bold ${getScoreColor(result.overall_score)}`}>
                      {result.overall_score.toFixed(1)}
                    </div>
                    <div className="text-sm text-gray-600">Overall Score</div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-3 gap-4 mb-6">
                  <div>
                    <div className="text-sm text-gray-600 mb-1">Technical (40%)</div>
                    <Progress value={result.weighted_scores.technical} className="h-2 mb-1" />
                    <div className={`text-lg font-semibold ${getScoreColor(result.weighted_scores.technical)}`}>
                      {result.weighted_scores.technical.toFixed(1)}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 mb-1">Risk (30%)</div>
                    <Progress value={result.weighted_scores.risk} className="h-2 mb-1" />
                    <div className={`text-lg font-semibold ${getScoreColor(result.weighted_scores.risk)}`}>
                      {result.weighted_scores.risk.toFixed(1)}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 mb-1">Financial (30%)</div>
                    <Progress value={result.weighted_scores.financial} className="h-2 mb-1" />
                    <div className={`text-lg font-semibold ${getScoreColor(result.weighted_scores.financial)}`}>
                      {result.weighted_scores.financial.toFixed(1)}
                    </div>
                  </div>
                </div>

                {/* Executive Summary */}
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h3 className="font-semibold mb-2 flex items-center gap-2">
                    <FileText className="w-4 h-4" />
                    Executive Summary
                  </h3>
                  <div className="text-sm whitespace-pre-line">{result.executive_summary}</div>
                </div>
              </CardContent>
            </Card>

            {/* Final Recommendation */}
            <Card className={`border-2 ${
              result.final_recommendation.decision === 'RECOMMEND_AWARD' ? 'border-green-300 bg-green-50' :
              result.final_recommendation.decision === 'REJECT' ? 'border-red-300 bg-red-50' :
              'border-yellow-300 bg-yellow-50'
            }`}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {result.final_recommendation.decision === 'RECOMMEND_AWARD' ? (
                    <CheckCircle className="w-6 h-6 text-green-600" />
                  ) : result.final_recommendation.decision === 'REJECT' ? (
                    <XCircle className="w-6 h-6 text-red-600" />
                  ) : (
                    <AlertTriangle className="w-6 h-6 text-yellow-600" />
                  )}
                  Final Recommendation
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-4">
                  <div>
                    <div className="text-sm text-gray-600">Decision</div>
                    {getStatusBadge(result.final_recommendation.decision)}
                  </div>
                  <Separator orientation="vertical" className="h-8" />
                  <div>
                    <div className="text-sm text-gray-600">Confidence</div>
                    <Badge variant="outline">{result.final_recommendation.confidence}</Badge>
                  </div>
                  <Separator orientation="vertical" className="h-8" />
                  <div>
                    <div className="text-sm text-gray-600">Human Approval Required</div>
                    <Badge variant={result.final_recommendation.requires_human_approval ? "destructive" : "default"}>
                      {result.final_recommendation.requires_human_approval ? 'Yes' : 'No'}
                    </Badge>
                  </div>
                </div>

                <div>
                  <div className="text-sm font-semibold text-gray-700 mb-1">Reason:</div>
                  <p className="text-sm">{result.final_recommendation.reason}</p>
                </div>

                <div>
                  <div className="text-sm font-semibold text-gray-700 mb-2">Next Steps:</div>
                  <ul className="list-disc list-inside space-y-1">
                    {result.final_recommendation.next_steps.map((step, idx) => (
                      <li key={idx} className="text-sm">{step}</li>
                    ))}
                  </ul>
                </div>
              </CardContent>
            </Card>

            {/* Detailed Analysis Tabs */}
            <Card>
              <CardHeader>
                <CardTitle>Detailed Agent Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="technical" className="w-full">
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="technical">Technical</TabsTrigger>
                    <TabsTrigger value="risk">Risk</TabsTrigger>
                    <TabsTrigger value="financial">Financial</TabsTrigger>
                  </TabsList>

                  {/* Technical Analysis Tab */}
                  <TabsContent value="technical" className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-semibold">Technical Compliance Analysis</h3>
                      {getStatusBadge(result.technical_analysis.status)}
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-semibold mb-2">Extracted Specifications</h4>
                        <div className="space-y-1 text-sm">
                          {Object.entries(result.technical_analysis.extracted_specs).map(([key, value]) => (
                            <div key={key} className="flex justify-between">
                              <span className="text-gray-600">{key.replace(/_/g, ' ')}:</span>
                              <span className="font-medium">{typeof value === 'number' ? value.toFixed(2) : value}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-semibold mb-2">SOP Parameters</h4>
                        <div className="space-y-1 text-sm">
                          {Object.entries(result.technical_analysis.sop_parameters).map(([key, value]: [string, any]) => (
                            <div key={key} className="flex justify-between">
                              <span className="text-gray-600">{key.replace(/_/g, ' ')}:</span>
                              <span className="font-medium">{value.min}-{value.max} {value.unit}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>

                    {result.technical_analysis.deviations.length > 0 && (
                      <div className="bg-red-50 p-4 rounded-lg">
                        <h4 className="font-semibold mb-2 text-red-800">Deviations Found</h4>
                        <div className="space-y-2">
                          {result.technical_analysis.deviations.map((dev, idx) => (
                            <div key={idx} className="text-sm">
                              <div className="font-medium">{dev.parameter.replace(/_/g, ' ')}</div>
                              <div className="text-gray-600">
                                Value: {dev.value.toFixed(2)} | SOP Range: {dev.sop_range} | 
                                Deviation: {dev.deviation_pct.toFixed(1)}%
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </TabsContent>

                  {/* Risk Assessment Tab */}
                  <TabsContent value="risk" className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-semibold">Risk Assessment</h3>
                      {getStatusBadge(result.risk_assessment.status)}
                    </div>

                    <div className="grid md:grid-cols-3 gap-4">
                      <div className="bg-gray-50 p-4 rounded-lg text-center">
                        <div className="text-2xl font-bold text-blue-600">{result.risk_assessment.financial_score}</div>
                        <div className="text-sm text-gray-600">Financial Score</div>
                      </div>
                      <div className="bg-gray-50 p-4 rounded-lg text-center">
                        <div className="text-2xl font-bold text-green-600">{result.risk_assessment.esg_score}</div>
                        <div className="text-sm text-gray-600">ESG Score</div>
                      </div>
                      <div className="bg-gray-50 p-4 rounded-lg text-center">
                        <div className={`text-2xl font-bold ${getScoreColor(result.risk_assessment.overall_risk_score)}`}>
                          {result.risk_assessment.overall_risk_score.toFixed(1)}
                        </div>
                        <div className="text-sm text-gray-600">Overall Risk Score</div>
                      </div>
                    </div>

                    {result.risk_assessment.red_flags.length > 0 && (
                      <Alert variant="destructive">
                        <AlertTriangle className="h-4 w-4" />
                        <AlertDescription>
                          <div className="font-semibold mb-1">Red Flags Detected:</div>
                          <ul className="list-disc list-inside">
                            {result.risk_assessment.red_flags.map((flag, idx) => (
                              <li key={idx}>{flag}</li>
                            ))}
                          </ul>
                        </AlertDescription>
                      </Alert>
                    )}

                    <div className="bg-blue-50 p-4 rounded-lg">
                      <div className="font-semibold mb-1">Recommendation:</div>
                      <p className="text-sm">{result.risk_assessment.recommendation}</p>
                    </div>
                  </TabsContent>

                  {/* Financial Analysis Tab */}
                  <TabsContent value="financial" className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-semibold">Financial Analysis</h3>
                      {getStatusBadge(result.financial_analysis.status)}
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-semibold mb-2 flex items-center gap-2">
                          <DollarSign className="w-4 h-4" />
                          Should-Cost Breakdown
                        </h4>
                        <div className="space-y-1 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600">Material Cost:</span>
                            <span className="font-medium">${result.financial_analysis.should_cost_breakdown.material_cost.toFixed(2)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Labor Cost:</span>
                            <span className="font-medium">${result.financial_analysis.should_cost_breakdown.labor_cost.toFixed(2)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Target Margin:</span>
                            <span className="font-medium">{result.financial_analysis.should_cost_breakdown.target_margin}</span>
                          </div>
                          <Separator className="my-2" />
                          <div className="flex justify-between font-semibold">
                            <span>Total Should-Cost:</span>
                            <span>${result.financial_analysis.should_cost_breakdown.total_should_cost.toFixed(2)}</span>
                          </div>
                        </div>
                      </div>

                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-semibold mb-2">Bid Comparison</h4>
                        <div className="space-y-1 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600">Bid Price:</span>
                            <span className="font-medium">${result.financial_analysis.bid_price.toFixed(2)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Quantity:</span>
                            <span className="font-medium">{result.financial_analysis.quantity} units</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Variance:</span>
                            <span className={`font-medium ${
                              Math.abs(result.financial_analysis.variance) <= 15 ? 'text-green-600' : 'text-red-600'
                            }`}>
                              {result.financial_analysis.variance > 0 ? '+' : ''}{result.financial_analysis.variance.toFixed(1)}%
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Threshold:</span>
                            <span className="font-medium">{result.financial_analysis.variance_threshold}</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="bg-blue-50 p-4 rounded-lg">
                      <div className="font-semibold mb-1">Recommendation:</div>
                      <p className="text-sm">{result.financial_analysis.recommendation}</p>
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default IntelligenceHub;