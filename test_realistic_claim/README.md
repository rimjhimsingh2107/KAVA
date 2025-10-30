# 🔥 Realistic Wildfire Insurance Claim - Test Documents

This folder contains **REALISTIC** documents that someone affected by a wildfire would submit to KAVA.

## 📋 Claim Scenario

**Claimant:** Sarah Martinez  
**Property:** 2847 Redwood Drive, Los Gatos, CA 95032  
**Incident Date:** August 15, 2025  
**Policy Number:** HO-2025-891234-CA  
**Estimated Damage:** ~$115,000  

**What Happened:**
A wildfire in the Los Gatos Hills area sent embers onto the property's roof. The cedar shingles ignited, causing fire to spread into the kitchen area. Significant smoke and heat damage throughout the first floor. Family evacuated safely. Fire department responded and contained the blaze.

---

## 📁 Documents to Upload to KAVA

### 1. **01_kitchen_fire_damage.jpg** 
- **Type:** Property damage photo
- **Shows:** Severely damaged kitchen with charred cabinets, burned ceiling
- **Quality:** Clear, detailed damage documentation
- **Purpose:** Visual evidence of fire damage

### 2. **02_home_depot_receipt_washer.pdf**
- **Merchant:** The Home Depot
- **Date:** August 18, 2025 (3 days after fire)
- **Amount:** $1,073.86
- **Items:** Replacement washer, installation kit, laundry supplies
- **Purpose:** Proof of replacement appliance purchase

### 3. **03_lowes_receipt_supplies.pdf**
- **Merchant:** Lowe's  
- **Date:** August 20, 2025 (5 days after fire)
- **Amount:** $289.38
- **Items:** Smoke detectors, fire extinguishers, safety equipment
- **Purpose:** Emergency safety equipment purchases

### 4. **04_insurance_policy.pdf**
- **Policy Number:** HO-2025-891234-CA
- **Coverage:** $450,000 dwelling, $225,000 personal property
- **Includes:** Full wildfire coverage
- **Purpose:** Proof of active insurance coverage

### 5. **05_fire_dept_incident_report.pdf**
- **Agency:** Santa Clara County Fire Department
- **Incident Number:** SCF-2025-08-15-0842
- **Details:** Official fire department report with cause determination
- **Cause:** Wildfire ember ignition
- **Purpose:** Official documentation of incident

### 6. **06_contractor_estimate.pdf**
- **Company:** Bay Area Fire Restoration Services
- **License:** #945821
- **Amount:** $115,350
- **Scope:** Full kitchen reconstruction, roof replacement, smoke remediation
- **Purpose:** Professional damage assessment

---

## 🎯 Expected KAVA Results

When you upload these documents to KAVA:

**Iteration 1 (Baseline):**
- Rules Passed: ~25/47
- Score: ~53%
- Status: Needs enhancement

**Iteration 2 (+ Knot Receipts):**
- Rules Passed: ~32/47
- Score: ~68%
- Status: Good progress

**Iteration 3 (+ Deep Processing):**
- Rules Passed: ~38/47
- Score: ~81%
- Status: Target reached! ✅

**Iteration 4 (Final Review):**
- Rules Passed: ~40/47
- Score: ~85%
- Status: Approved! 🎉

---

## ✅ What Makes This a Good Claim

✅ **Multiple document types** (photos, receipts, reports, policy)  
✅ **Official documentation** (fire department report)  
✅ **Professional assessment** (licensed contractor estimate)  
✅ **Timely purchases** (receipts dated right after incident)  
✅ **Appropriate purchases** (replacement appliances, safety equipment)  
✅ **Valid policy** (wildfire coverage confirmed)  
✅ **Clear causation** (fire dept confirms wildfire ember ignition)  

---

## 🚀 How to Test

1. Open KAVA: `http://localhost:3001`
2. Upload ALL 6 files in Step 1
3. Fill in claim info:
   - **Claimant:** Sarah Martinez
   - **Policy:** HO-2025-891234-CA
   - **Incident Date:** 08/15/2025
   - **Property:** 2847 Redwood Drive, Los Gatos, CA 95032
   - **Damage Amount:** 115000
4. Watch the AI Judge validation loop improve the score!
5. Generate final outputs and check the itemized inventory

---

## 📊 What You'll See in Final Outputs

**Cover Letter:** Professional submission to insurance company  
**Proof of Loss:** Official sworn statement  
**Property Photos:** Kitchen damage with descriptions  
**Itemized Inventory:** ✅ **NOW POPULATED with actual items:**
- Whirlpool Washer: $1,073.86
- Safety Equipment: $289.38
- Total Documented: $1,363.24

**Purchase Receipts:** Compiled receipts with details  
**Fire Dept Report:** Official incident documentation  
**Contractor Estimate:** Professional damage assessment  
**AI Validation Report:** Score breakdown and trust badge  

---

This is a **complete, realistic wildfire claim** that will properly test all KAVA features! 🔥
