// Mock data generation for BioSure - Carvykti Outcomes Desk

export interface Patient {
  id: string;
  age: number;
  sex: 'M' | 'F';
  state: string;
  region: string;
  payerType: 'Commercial' | 'Medicare Advantage' | 'Medicaid' | 'Other';
  indexDate: Date;
  treatingHcoId: string;
  treatingHcoName: string;
  priorLines: number;
  hasEvent12Month: boolean;
  hasRetreatrment18Month: boolean;
  hasToxicity30Day: boolean;
}

export interface HCO {
  id: string;
  name: string;
  state: string;
  region: string;
  treatedPatients: number;
  ghostPatients: number;
}

export interface ContractTemplate {
  id: string;
  name: string;
  description: string;
  outcomeType: '12-month-survival' | 'retreatment' | 'toxicity';
  defaultTimeWindow: number;
  defaultRebatePercent: number;
}

const US_STATES = ['CA', 'TX', 'FL', 'NY', 'PA', 'IL', 'OH', 'GA', 'NC', 'MI'];
const REGIONS = ['West', 'South', 'Northeast', 'Midwest'];
const PAYER_TYPES: Patient['payerType'][] = ['Commercial', 'Medicare Advantage', 'Medicaid', 'Other'];

const HCO_NAMES = [
  'Memorial Cancer Center',
  'City General Hospital',
  'University Medical Center',
  'Regional Health System',
  'Cancer Treatment Institute',
  'Academic Medical Center',
  'Community Hospital',
  'Comprehensive Cancer Center',
  'Medical Center of Excellence',
  'Specialty Oncology Clinic'
];

// Generate mock patients
export const generateMockPatients = (count: number = 847): Patient[] => {
  const patients: Patient[] = [];
  const today = new Date();
  
  for (let i = 0; i < count; i++) {
    const indexDate = new Date(today);
    indexDate.setDate(indexDate.getDate() - Math.floor(Math.random() * 730)); // Last 2 years
    
    const age = 55 + Math.floor(Math.random() * 25); // 55-80 years
    const state = US_STATES[Math.floor(Math.random() * US_STATES.length)];
    const region = REGIONS[Math.floor(Math.random() * REGIONS.length)];
    const payerType = PAYER_TYPES[Math.floor(Math.random() * PAYER_TYPES.length)];
    const priorLines = 2 + Math.floor(Math.random() * 4); // 2-5 prior lines
    
    // Outcome probabilities (clinically plausible)
    const hasEvent12Month = Math.random() < 0.25; // 25% event rate
    const hasRetreatrment18Month = Math.random() < 0.15; // 15% retreatment rate
    const hasToxicity30Day = Math.random() < 0.12; // 12% toxicity rate
    
    const hcoIndex = Math.floor(Math.random() * 50);
    
    patients.push({
      id: `PT-${String(i + 1).padStart(6, '0')}`,
      age,
      sex: Math.random() > 0.4 ? 'M' : 'F',
      state,
      region,
      payerType,
      indexDate,
      treatingHcoId: `HCO-${String(hcoIndex + 1).padStart(3, '0')}`,
      treatingHcoName: `${HCO_NAMES[hcoIndex % HCO_NAMES.length]} - ${state}`,
      priorLines,
      hasEvent12Month,
      hasRetreatrment18Month,
      hasToxicity30Day
    });
  }
  
  return patients;
};

// Generate mock HCOs with ghost patients
export const generateMockHCOs = (patients: Patient[]): HCO[] => {
  const hcoMap = new Map<string, HCO>();
  
  // Count treated patients per HCO
  patients.forEach(patient => {
    if (!hcoMap.has(patient.treatingHcoId)) {
      hcoMap.set(patient.treatingHcoId, {
        id: patient.treatingHcoId,
        name: patient.treatingHcoName,
        state: patient.state,
        region: patient.region,
        treatedPatients: 0,
        ghostPatients: 0
      });
    }
    const hco = hcoMap.get(patient.treatingHcoId)!;
    hco.treatedPatients++;
  });
  
  // Add ghost patients (eligible but untreated)
  hcoMap.forEach(hco => {
    // Ghost patients typically 2-5x the treated count
    hco.ghostPatients = Math.floor(hco.treatedPatients * (2 + Math.random() * 3));
  });
  
  return Array.from(hcoMap.values()).sort((a, b) => b.ghostPatients - a.ghostPatients);
};

// Contract templates
export const CONTRACT_TEMPLATES: ContractTemplate[] = [
  {
    id: 'survival-12m',
    name: '12-Month Survival Warranty',
    description: 'Rebate if patient dies or escalates to new MM treatment before 12 months',
    outcomeType: '12-month-survival',
    defaultTimeWindow: 12,
    defaultRebatePercent: 50
  },
  {
    id: 'retreatment-18m',
    name: 'Retreatment Warranty',
    description: 'Rebate if patient receives new high-cost MM treatment within 18 months',
    outcomeType: 'retreatment',
    defaultTimeWindow: 18,
    defaultRebatePercent: 40
  },
  {
    id: 'toxicity-30d',
    name: 'Toxicity Warranty',
    description: 'Rebate if patient has ICU/inpatient readmission with CRS/ICANS within 30 days',
    outcomeType: 'toxicity',
    defaultTimeWindow: 1,
    defaultRebatePercent: 30
  }
];

// Initialize and cache data
let cachedPatients: Patient[] | null = null;
let cachedHCOs: HCO[] | null = null;

export const getPatients = (): Patient[] => {
  if (!cachedPatients) {
    cachedPatients = generateMockPatients();
  }
  return cachedPatients;
};

export const getHCOs = (): HCO[] => {
  if (!cachedHCOs) {
    cachedHCOs = generateMockHCOs(getPatients());
  }
  return cachedHCOs;
};