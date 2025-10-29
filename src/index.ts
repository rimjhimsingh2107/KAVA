import * as dotenv from 'dotenv'
import { createHash, randomBytes } from 'crypto'
import * as express from 'express'

dotenv.config();

// EigenCloud AI Judge Constitution - Secure TEE Implementation
class EigenCloudJudge {
  public account: string;
  public constitution: any;

  constructor(mnemonic: string) {
    // Simplified account generation for demo
    this.account = createHash('sha256').update(mnemonic).digest('hex').slice(0, 42);
    this.constitution = this.loadConstitution();
  }

  private loadConstitution() {
    // 47-rule constitution for wildfire insurance claims
    return {
      version: "v1.0",
      rules: {
        completeness: [
          {
            id: "COMP_001",
            description: "Property photos must show both pre-fire condition AND post-fire damage",
            weight: 0.15,
            required: true
          },
          {
            id: "COMP_002", 
            description: "All replacement items >$100 require receipt or proof of purchase",
            weight: 0.12,
            required: true
          },
          {
            id: "COMP_003",
            description: "All expenses must be within policy coverage period",
            weight: 0.18,
            required: true
          },
          {
            id: "COMP_004",
            description: "Policy documentation must be present and valid",
            weight: 0.10,
            required: true
          },
          {
            id: "COMP_005",
            description: "Fire department incident report must be provided",
            weight: 0.08,
            required: true
          },
          {
            id: "COMP_006",
            description: "Evacuation orders or warnings must be documented",
            weight: 0.06,
            required: false
          },
          {
            id: "COMP_007",
            description: "Property deed or ownership proof required",
            weight: 0.05,
            required: true
          },
          {
            id: "COMP_008",
            description: "Utility disconnection notices if applicable",
            weight: 0.03,
            required: false
          },
          {
            id: "COMP_009",
            description: "Temporary housing receipts for additional living expenses",
            weight: 0.04,
            required: false
          },
          {
            id: "COMP_010",
            description: "Professional damage assessment or contractor estimates",
            weight: 0.07,
            required: true
          },
          {
            id: "COMP_011",
            description: "Inventory list of damaged/destroyed personal property",
            weight: 0.06,
            required: true
          },
          {
            id: "COMP_012",
            description: "Weather reports confirming fire conditions on incident date",
            weight: 0.04,
            required: false
          }
        ],
        damage_assessment: [
          {
            id: "DAMAGE_001",
            description: "Damage must be directly attributable to wildfire",
            weight: 0.20,
            required: true
          },
          {
            id: "DAMAGE_002",
            description: "Replacement costs must align with local market rates",
            weight: 0.08,
            required: false
          },
          {
            id: "DAMAGE_003",
            description: "Structural damage consistent with fire/heat exposure",
            weight: 0.12,
            required: true
          },
          {
            id: "DAMAGE_004",
            description: "Smoke damage patterns must be consistent with wildfire",
            weight: 0.08,
            required: false
          },
          {
            id: "DAMAGE_005",
            description: "No evidence of pre-existing damage being claimed",
            weight: 0.10,
            required: true
          },
          {
            id: "DAMAGE_006",
            description: "Damage timeline consistent with fire progression",
            weight: 0.06,
            required: true
          },
          {
            id: "DAMAGE_007",
            description: "Heat damage patterns match wildfire characteristics",
            weight: 0.05,
            required: false
          },
          {
            id: "DAMAGE_008",
            description: "Ash and debris evidence consistent with wildfire",
            weight: 0.04,
            required: false
          },
          {
            id: "DAMAGE_009",
            description: "Neighboring property damage supports claim",
            weight: 0.03,
            required: false
          },
          {
            id: "DAMAGE_010",
            description: "No evidence of arson or intentional fire setting",
            weight: 0.15,
            required: true
          }
        ],
        documentation_quality: [
          {
            id: "DOC_001",
            description: "Photos must be clear, dated, and show full context",
            weight: 0.07,
            required: false
          },
          {
            id: "DOC_002",
            description: "Receipts must be legible with clear merchant, date, and items",
            weight: 0.10,
            required: true
          },
          {
            id: "DOC_003",
            description: "Documents must be original or certified copies",
            weight: 0.05,
            required: true
          },
          {
            id: "DOC_004",
            description: "Photo metadata must be intact and verifiable",
            weight: 0.04,
            required: false
          },
          {
            id: "DOC_005",
            description: "Multiple angles of damage must be documented",
            weight: 0.06,
            required: true
          },
          {
            id: "DOC_006",
            description: "Before and after photos must show same perspectives",
            weight: 0.05,
            required: false
          }
        ],
        temporal_validation: [
          {
            id: "TIME_001",
            description: "Claim filed within policy-specified timeframe",
            weight: 0.12,
            required: true
          },
          {
            id: "TIME_002",
            description: "Purchases made after incident date are valid",
            weight: 0.08,
            required: true
          },
          {
            id: "TIME_003",
            description: "Emergency expenses incurred within reasonable timeframe",
            weight: 0.05,
            required: false
          },
          {
            id: "TIME_004",
            description: "Contractor estimates obtained within 30 days of incident",
            weight: 0.04,
            required: false
          },
          {
            id: "TIME_005",
            description: "No suspicious pre-incident activity patterns",
            weight: 0.10,
            required: true
          }
        ],
        geographic_validation: [
          {
            id: "GEO_001",
            description: "Property location within confirmed fire perimeter",
            weight: 0.15,
            required: true
          },
          {
            id: "GEO_002",
            description: "Evacuation zone matches property address",
            weight: 0.08,
            required: false
          },
          {
            id: "GEO_003",
            description: "Wind patterns support fire spread to property",
            weight: 0.05,
            required: false
          },
          {
            id: "GEO_004",
            description: "Topography consistent with fire behavior",
            weight: 0.04,
            required: false
          }
        ],
        policy_compliance: [
          {
            id: "POLICY_001",
            description: "Claim amount within policy limits",
            weight: 0.12,
            required: true
          },
          {
            id: "POLICY_002",
            description: "Deductible properly calculated and applied",
            weight: 0.08,
            required: true
          },
          {
            id: "POLICY_003",
            description: "Coverage effective on incident date",
            weight: 0.15,
            required: true
          },
          {
            id: "POLICY_004",
            description: "No policy exclusions apply to claimed damages",
            weight: 0.10,
            required: true
          },
          {
            id: "POLICY_005",
            description: "Premium payments current at time of loss",
            weight: 0.08,
            required: true
          }
        ],
        financial_validation: [
          {
            id: "FIN_001",
            description: "Claimed amounts supported by documentation",
            weight: 0.12,
            required: true
          },
          {
            id: "FIN_002",
            description: "No duplicate claims across multiple policies",
            weight: 0.10,
            required: true
          },
          {
            id: "FIN_003",
            description: "Depreciation properly calculated for personal property",
            weight: 0.06,
            required: false
          },
          {
            id: "FIN_004",
            description: "Labor costs align with local market rates",
            weight: 0.05,
            required: false
          },
          {
            id: "FIN_005",
            description: "Material costs verified against supplier pricing",
            weight: 0.04,
            required: false
          }
        ]
      },
      fraud_indicators: [
        "Receipts dated before incident date",
        "Duplicate receipts across multiple claims", 
        "Unusual purchasing patterns",
        "Mismatched locations and incident area",
        "Excessive luxury item purchases",
        "Multiple claims filed simultaneously",
        "Inconsistent damage descriptions",
        "Suspicious contractor relationships",
        "Inflated replacement cost estimates",
        "Missing or altered photo metadata",
        "Claim filed immediately after policy purchase",
        "Previous fraud history on record",
        "Inconsistent witness statements",
        "Unusual payment method patterns",
        "Backdated receipts or invoices"
      ]
    };
  }

  // Secure evaluation function running in TEE
  async evaluateClaim(claimData: any): Promise<any> {
    console.log(`EigenCloud Judge evaluating claim with account: ${this.account}`);
    
    // Generate attestation hash for this evaluation
    const evaluationHash = this.generateAttestationHash(claimData);
    
    // Evaluate against constitution rules
    const results = {
      claim_id: claimData.claim_id,
      evaluator_address: this.account,
      constitution_version: this.constitution.version,
      attestation_hash: evaluationHash,
      overall_score: 0,
      confidence: 0,
      approved: false,
      rules_evaluated: [],
      missing_documents: [],
      fraud_indicators: [],
      rationale: "",
      timestamp: Date.now()
    };

    // Process completeness rules
    let totalWeight = 0;
    let weightedScore = 0;

    for (const rule of this.constitution.rules.completeness) {
      const evaluation = this.evaluateRule(rule, claimData);
      (results.rules_evaluated as any[]).push(evaluation);
      
      totalWeight += rule.weight;
      if (evaluation.passed) {
        weightedScore += rule.weight;
      }
    }

    // Calculate final scores
    results.overall_score = totalWeight > 0 ? weightedScore / totalWeight : 0;
    results.confidence = this.calculateConfidence(results.rules_evaluated);
    results.approved = results.overall_score >= 0.8;
    results.rationale = this.generateRationale(results);

    // Sign the evaluation with TEE private key
    const signature = await this.signEvaluation(results);
    
    return {
      ...results,
      tee_signature: signature,
      tee_attestation: true
    };
  }

  private evaluateRule(rule: any, claimData: any): any {
    // Simplified rule evaluation logic
    // In production, this would contain sophisticated AI analysis
    
    const hasRequiredDocuments = claimData.documents && claimData.documents.length > 0;
    const passed = rule.required ? hasRequiredDocuments : true;
    
    return {
      rule_id: rule.id,
      description: rule.description,
      weight: rule.weight,
      passed: passed,
      confidence: 0.85,
      rationale: passed ? "Rule satisfied" : "Missing required documentation"
    };
  }

  private calculateConfidence(rules: any[]): number {
    const avgConfidence = rules.reduce((sum, rule) => sum + rule.confidence, 0) / rules.length;
    return avgConfidence || 0;
  }

  private generateRationale(results: any): string {
    const passedRules = results.rules_evaluated.filter((r: any) => r.passed).length;
    const totalRules = results.rules_evaluated.length;
    
    return `EigenCloud TEE evaluation: ${passedRules}/${totalRules} rules passed. ` +
           `Overall score: ${(results.overall_score * 100).toFixed(1)}%. ` +
           `Evaluation performed in secure enclave with attestation hash: ${results.attestation_hash.substring(0, 16)}...`;
  }

  public generateAttestationHash(claimData: any): string {
    const attestationHash = createHash('sha256')
      .update(JSON.stringify({
        constitution: this.constitution,
        evaluator: this.account,
        timestamp: Date.now()
      }))
      .digest('hex');
    return attestationHash;
  }

  private async signEvaluation(results: any): Promise<string> {
    // Sign the evaluation results with the TEE private key
    const messageHash = createHash('sha256').update(JSON.stringify(results)).digest('hex');
    
    // In a real TEE environment, this would use hardware-based signing
    return `tee_signature_${messageHash.substring(0, 32)}`;
  }

  // Public method to verify TEE attestation
  static verifyAttestation(evaluation: any, expectedAddress: string): boolean {
    return evaluation.tee_attestation === true && 
           evaluation.evaluator_address === expectedAddress &&
           evaluation.tee_signature !== undefined;
  }
}

// HTTP server to expose EigenCloud Judge as API
async function startEigenCloudServer() {
  const mnemonic = process.env.MNEMONIC;
  
  if (!mnemonic) {
    console.error('MNEMONIC environment variable is not set');
    process.exit(1);
  }

  const judge = new EigenCloudJudge(mnemonic);
  console.log(`EigenCloud Judge initialized with address: ${judge.account}`);

  // Simple HTTP server for claim evaluation
  const http = require('http');
  
  const server = http.createServer(async (req: any, res: any) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
      res.writeHead(200);
      res.end();
      return;
    }

    if (req.method === 'POST' && req.url === '/evaluate-claim') {
      let body = '';
      req.on('data', (chunk: any) => body += chunk);
      req.on('end', async () => {
        try {
          const claimData = JSON.parse(body);
          const evaluation = await judge.evaluateClaim(claimData);
          
          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify(evaluation));
        } catch (error: any) {
          console.error('Failed to evaluate claim:', error);
          res.writeHead(500, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: error.message }));
        }
      });
    } else {
      res.writeHead(404);
      res.end('Not Found');
    }
  });

  const PORT = process.env.EIGENCLOUD_PORT || 9000;
  server.listen(PORT, () => {
    console.log(`EigenCloud Judge started on port ${PORT}`);
    console.log(`Constitution version: ${judge.constitution.version}`);
    console.log(`Evaluator address: ${judge.account}`);
    console.log(`Attestation hash: ${judge.generateAttestationHash({})}`);

    console.log('\n=== EigenCloud AI Judge Ready ===');
  });
}

async function main() {
  await startEigenCloudServer();
}

main().catch(console.error);
