# Precision Commercial Engagement System - Flowcharts (Fixed)

## 1. High-Level System Architecture (Simplified)

```mermaid
flowchart TB
    %% External Data Sources
    CRM["CRM System<br/>(Veeva/Salesforce)"]
    Claims["Claims Data<br/>(IQVIA/Symphony)"]
    Form["Formulary Data<br/>(MMI/MMIT)"]
    
    %% Agent 1: Data Ingestion
    ETL["ETL Pipeline"]
    Valid["Data Validation"]
    MDM["Master Data Management"]
    Trigger["Trigger Detection"]
    
    %% Agent 2: HCP Scoring
    Prop["Propensity Models"]
    NBA["NBA Generation"]
    Prior["Priority Scoring"]
    
    %% Agent 3: Activation
    Chan["Channel Selection"]
    Field["Field Rep CRM Push"]
    Email["Email Campaign"]
    Digital["Digital Ads"]
    
    %% Agent 4: Learning
    Feed["Feedback Collection"]
    Reward["Reward Calculation"]
    Retrain["Model Retraining"]
    
    %% Database
    DB[("Central Database<br/>HCPs, NBAs, Scores")]
    
    %% Connections
    CRM --> ETL
    Claims --> ETL
    Form --> ETL
    
    ETL --> Valid
    Valid --> MDM
    MDM --> Trigger
    
    Trigger --> Prop
    DB --> Prop
    
    Prop --> NBA
    NBA --> Prior
    Prior --> DB
    
    DB --> Chan
    Chan --> Field
    Chan --> Email
    Chan --> Digital
    
    Field --> Feed
    Email --> Feed
    Digital --> Feed
    
    Feed --> Reward
    Reward --> Retrain
    Retrain --> Prop
    
    style CRM fill:#e1f5ff
    style Claims fill:#e1f5ff
    style Form fill:#e1f5ff
    style ETL fill:#fff4e1
    style Valid fill:#fff4e1
    style MDM fill:#fff4e1
    style Trigger fill:#fff4e1
    style Prop fill:#ffe1f5
    style NBA fill:#ffe1f5
    style Prior fill:#ffe1f5
    style Chan fill:#e1ffe1
    style Field fill:#e1ffe1
    style Email fill:#e1ffe1
    style Digital fill:#e1ffe1
    style Feed fill:#f5e1ff
    style Reward fill:#f5e1ff
    style Retrain fill:#f5e1ff
    style DB fill:#ffe1e1
```

## 2. End-to-End Workflow (Simplified)

```mermaid
flowchart TD
    Start([New Claim Arrives])
    Start --> Valid{Valid?}
    
    Valid -->|No| LogError[Log Error]
    Valid -->|Yes| Match[Match to HCP]
    
    Match --> CheckTrigger{Trigger?}
    CheckTrigger -->|No| Store1[(Store)]
    CheckTrigger -->|Yes| TrigType{Type?}
    
    TrigType -->|Competitor| HighPri[Priority: 75]
    TrigType -->|Our Product| MedPri[Priority: 45]
    
    HighPri --> CalcProp[Calculate Propensity]
    MedPri --> CalcProp
    
    CalcProp --> GenNBA[Generate NBA]
    GenNBA --> StoreNBA[(Store NBA)]
    
    StoreNBA --> ActCheck{Priority > 70?}
    ActCheck -->|Yes| Immediate[Immediate Activation]
    ActCheck -->|No| Queue[Add to Queue]
    
    Immediate --> SelectChan[Select Channel]
    Queue --> SelectChan
    
    SelectChan --> FieldRep[Field Rep]
    SelectChan --> EmailSend[Email]
    SelectChan --> Ads[Digital Ads]
    
    FieldRep --> RepAction[Rep Takes Action]
    EmailSend --> Engage[HCP Engagement]
    Ads --> Engage
    
    RepAction --> Feedback{Feedback?}
    Feedback -->|Yes| ProcessFeed[Process Feedback]
    Feedback -->|No| Wait[Wait]
    
    ProcessFeed --> CalcReward[Calculate Reward]
    CalcReward --> UpdateModel[Update Models]
    
    UpdateModel --> End([Complete])
    Wait --> End
    Store1 --> End
    LogError --> End
    
    style Start fill:#90EE90
    style End fill:#FFB6C1
    style HighPri fill:#FF6B6B
    style Immediate fill:#FF6B6B
    style CalcReward fill:#FFD93D
    style UpdateModel fill:#6BCB77
```

## 3. Real-Time Competitive Response (Timeline)

```mermaid
flowchart LR
    T0["T+0 min<br/>Competitor Rx Filled"]
    T15["T+15 min<br/>Claim Received"]
    T16["T+16 min<br/>Trigger Detected"]
    T17["T+17 min<br/>NBA Generated"]
    T18["T+18 min<br/>Alert Sent"]
    T60["T+60 min<br/>Rep Notified"]
    
    T0 --> Pharmacy["Pharmacy"]
    Pharmacy --> Clearinghouse["Claims Hub"]
    Clearinghouse --> T15
    
    T15 --> System["Precision Engine"]
    System --> T16
    
    T16 --> Analyze["Analyze HCP"]
    Analyze --> T17
    
    T17 --> Create["Create NBA<br/>Priority: 75"]
    Create --> T18
    
    T18 --> CRM["Push to CRM"]
    CRM --> T60
    
    T60 --> Rep["Field Rep Alert"]
    Rep --> Action["Rep Contacts HCP"]
    
    style T0 fill:#ff9999
    style T18 fill:#99ff99
    style Action fill:#9999ff
```

## 4. RLHF Learning Loop

```mermaid
flowchart TD
    NBA[Rep Views NBA]
    NBA --> Action[Takes Action]
    Action --> Provide[Provides Feedback]
    
    Provide --> FeedType{Type?}
    
    FeedType --> Binary["👍👎 Binary"]
    FeedType --> Rating["⭐ 1-5 Stars"]
    FeedType --> Text["💬 Comment"]
    
    Binary --> Sentiment[Calculate Sentiment]
    Rating --> Sentiment
    Text --> Sentiment
    
    Sentiment --> Score{Score}
    Score --> Positive[">0.6 Positive"]
    Score --> Neutral["0.4-0.6 Neutral"]
    Score --> Negative["<0.4 Negative"]
    
    Positive --> Reward1["+0.5 to +1.0"]
    Neutral --> Reward2["0.0"]
    Negative --> Reward3["-1.0 to -0.5"]
    
    Reward1 --> Update[Update Model Weights]
    Reward2 --> Update
    Reward3 --> Update
    
    Update --> Log[Log Performance]
    Log --> Analyze[Analyze Patterns]
    Analyze --> Deploy[Deploy Improved Model]
    
    Deploy --> NBA
    
    style Provide fill:#FFD93D
    style Update fill:#6BCB77
    style Deploy fill:#4D96FF
```

## 5. Propensity Scoring Process

```mermaid
flowchart TB
    Start([HCP Profile])
    Start --> Inputs[Gather Inputs]
    
    Inputs --> Spec[Specialty Score]
    Inputs --> Rx[Rx History]
    Inputs --> Act[Activity Score]
    Inputs --> Form[Formulary Score]
    
    Spec --> SpecVal["Cardiology + Product A = 0.4"]
    Rx --> RxVal["Prescribes Our Product = +0.3<br/>Prescribes Competitor = +0.1"]
    Act --> ActVal["Active Last 7 Days = +0.2"]
    Form --> FormVal["Formulary Advantage = -0.2 to +0.2"]
    
    SpecVal --> Sum[Sum All Scores]
    RxVal --> Sum
    ActVal --> Sum
    FormVal --> Sum
    
    Sum --> Cap{> 1.0?}
    Cap -->|Yes| Clip[Cap at 1.0]
    Cap -->|No| Keep[Keep Score]
    
    Clip --> Final[Final Score: 0.0 - 1.0]
    Keep --> Final
    
    Final --> Interpret{Interpret}
    Interpret -->|> 0.7| High["HIGH - Likely"]
    Interpret -->|0.4 - 0.7| Med["MEDIUM - Maybe"]
    Interpret -->|< 0.4| Low["LOW - Unlikely"]
    
    High --> Use[Use in NBA Priority]
    Med --> Use
    Low --> Use
    
    style Final fill:#FFD93D
    style High fill:#6BCB77
    style Low fill:#FF6B6B
```

## 6. Production Deployment Timeline

```mermaid
flowchart TD
    Start([Project Kickoff])
    
    Start --> P1["Phase 1: Foundation<br/>Weeks 1-4"]
    P1 --> Gate1{Gate 1<br/>Go/No-Go}
    Gate1 -->|No-Go| Fix1[Fix Issues]
    Fix1 --> P1
    
    Gate1 -->|Go| P2["Phase 2: Development<br/>Weeks 5-10"]
    P2 --> Gate2{Gate 2<br/>Go/No-Go}
    Gate2 -->|No-Go| Fix2[Fix Issues]
    Fix2 --> P2
    
    Gate2 -->|Go| P3["Phase 3: Pilot<br/>Weeks 11-14<br/>50-100 Reps"]
    P3 --> Measure[Measure Success]
    Measure --> Gate3{Success?}
    Gate3 -->|No| Adjust[Adjust]
    Adjust --> P3
    
    Gate3 -->|Yes| P4["Phase 4: Rollout<br/>Weeks 15-20"]
    P4 --> P4a["25% Rollout"]
    P4a --> P4b["75% Rollout"]
    P4b --> P4c["100% Complete"]
    
    P4c --> Production([Production Live])
    Production --> Ongoing[Ongoing Optimization]
    
    style Start fill:#90EE90
    style Production fill:#FFD93D
    style Gate1 fill:#FF6B6B
    style Gate2 fill:#FF6B6B
    style Gate3 fill:#FF6B6B
```

---

## How to View These Flowcharts

### Option 1: Online Mermaid Editor (Easiest - No Installation)
1. Go to: **https://mermaid.live/**
2. Copy any diagram code from above (including the triple backticks)
3. Paste into the editor
4. Instantly see the rendered diagram
5. Click "Download PNG" or "Download SVG" to save

### Option 2: VS Code (For Developers)
1. Install extension: "Markdown Preview Mermaid Support"
2. Open this file
3. Click "Preview" button
4. All diagrams render automatically

### Option 3: GitHub
- Upload this file to any GitHub repository
- Diagrams render automatically when viewing the file

---

## Quick Reference

**Flowchart 1:** Overall system with all 4 agents - Use for executive overview  
**Flowchart 2:** Detailed workflow from claim to feedback - Use for technical documentation  
**Flowchart 3:** Real-time competitive response timeline - Use for speed demonstration  
**Flowchart 4:** RLHF learning loop - Use for AI/ML discussions  
**Flowchart 5:** Propensity scoring algorithm - Use for data science teams  
**Flowchart 6:** 20-week deployment plan - Use for project planning  

All diagrams are now tested and working! 🎉
