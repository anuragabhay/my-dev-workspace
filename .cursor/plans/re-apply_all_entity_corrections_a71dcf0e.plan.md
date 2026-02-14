---
name: Re-apply All Entity Corrections
overview: "Re-apply all code review corrections that were lost: remove column constraints, fix BaseEntity inheritance, remove audit field duplicates, and remove foreign key relationships."
todos: []
---

# Re-apply All Entity Corrections

## Current State Analysis

### Entity Inheritance Status (24 total entities)

**Correctly extending BaseEntity (8 entities):** ✅

- Agreement, Approvals, CaseIncident, Opportunity, OpportunityExtension, OrderManagement, Provisioning, Quote

**Extending BaseEntity BUT have duplicate audit fields (4 entities):** ⚠️

- AgreementDocument, CreditCheckApproval, CustomerInformation, SignAgreement

**Missing BaseEntity inheritance (1 entity):** ❌

- SignEvents (has audit fields but doesn't extend)

**Correctly extending BaseHistoryEntity (5 entities):** ✅

- AgreementStatusHistory, ApprovalsStatusHistory, CaseStatusHistory, OpportunityStatusHistory, QuoteStatusHistory

**Correctly extending BaseSummaryEntity (4 entities):** ✅

- AgreementFileSummary, AgreementStatusSummary, OpportunitySummary, QuoteStatusSummary

**Not extending any base (partial audit fields only) (2 entities):** ✅

- ActivityLog, Messages

### Issues to Fix

1. **Column constraints present in ALL 27 files** (24 entities + 3 base classes)
2. **SignEvents missing BaseEntity inheritance + has duplicate audit fields**
3. **4 entities have duplicate audit fields** (AgreementDocument, CreditCheckApproval, CustomerInformation, SignAgreement)
4. **SignEvents has @ManyToOne relationship** (must be removed)

## Changes to Apply

### Fix 1: Remove ALL Column Constraints (27 files)

**Target:** All files in [`src/main/java/com/adobe/dealtracker/entity/`](src/main/java/com/adobe/dealtracker/entity/)

Strip all parameters from `@Column` except `name`:

```java
// BEFORE:
@Column(name = "dr_number", length = 20)
@Column(name = "opportunityid", length = 36, nullable = false)
@Column(name = "tcv", precision = 15, scale = 2)

// AFTER:
@Column(name = "dr_number")
@Column(name = "opportunityid")
@Column(name = "tcv")
```

**Files:** All 24 entity files + 3 base entity files

### Fix 2: SignEvents - Add BaseEntity Inheritance

**File:** [`SignEvents.java`](src/main/java/com/adobe/dealtracker/entity/SignEvents.java)

1. Add import: `import com.adobe.dealtracker.entity.base.BaseEntity;`
2. Change: `public class SignEvents {` → `public class SignEvents extends BaseEntity {`
3. Remove @ManyToOne/@JoinColumn relationship block
4. Remove 6 duplicate audit fields (createdOn, createdBy, modifiedOn, modifiedBy, isDeleted, syncedAt)
5. Add comment: `// Audit fields inherited from BaseEntity`

### Fix 3: Remove Duplicate Audit Fields (4 files)

**Files:**

- [`AgreementDocument.java`](src/main/java/com/adobe/dealtracker/entity/AgreementDocument.java)
- [`CreditCheckApproval.java`](src/main/java/com/adobe/dealtracker/entity/CreditCheckApproval.java)
- [`CustomerInformation.java`](src/main/java/com/adobe/dealtracker/entity/CustomerInformation.java)
- [`SignAgreement.java`](src/main/java/com/adobe/dealtracker/entity/SignAgreement.java)

Remove these duplicate fields:

```java
@Column(name = "created_on")
private LocalDateTime createdOn;

@Column(name = "created_by")
private String createdBy;

@Column(name = "modified_on")
private LocalDateTime modifiedOn;

@Column(name = "modified_by")
private String modifiedBy;

@Column(name = "is_deleted")
private Boolean isDeleted = false;

@Column(name = "synced_at")
private LocalDateTime syncedAt;
```

Replace with:

```java
// Audit fields inherited from BaseEntity:
// - createdOn, createdBy, modifiedOn, modifiedBy, isDeleted, syncedAt
```

### Fix 4: Remove Column Constraints from Base Classes

**Files:**

- [`BaseEntity.java`](src/main/java/com/adobe/dealtracker/entity/base/BaseEntity.java) - Currently has constraints!
- [`BaseHistoryEntity.java`](src/main/java/com/adobe/dealtracker/entity/base/BaseHistoryEntity.java)
- [`BaseSummaryEntity.java`](src/main/java/com/adobe/dealtracker/entity/base/BaseSummaryEntity.java)

## Implementation Steps

**Step 1:** Remove column constraints from all 27 files

```bash
perl -i -pe 's/@Column\([^)]*name\s*=\s*"([^"]*)"[^)]*\)/@Column(name = "$1")/g' *.java base/*.java
```

**Step 2:** Fix SignEvents (Python script)

- Add BaseEntity import and inheritance
- Remove @ManyToOne block
- Remove audit fields
- Add inheritance comment

**Step 3:** Remove audit fields from 4 entities (Python script)

- Remove audit field declarations
- Add inheritance comment

## Verification Checklist

- [ ] No constraints in any @Column: `grep -c "nullable\|length\|precision" *.java base/*.java`
- [ ] SignEvents extends BaseEntity: `grep "class SignEvents extends" SignEvents.java`
- [ ] No @ManyToOne: `grep -c "@ManyToOne" *.java`
- [ ] All 5 entities have no audit fields: Check last 10 lines of each file
- [ ] All 13 main entities extend BaseEntity
- [ ] All 5 history entities extend BaseHistoryEntity
- [ ] All 4 summary entities extend BaseSummaryEntity
- [ ] Git status shows 27 modified files

## Summary

**Total files to modify:** 27

- 24 entity files
- 3 base entity files

**Total entities requiring audit field cleanup:** 5

- SignEvents (add extends + remove fields)
- AgreementDocument, CreditCheckApproval, CustomerInformation, SignAgreement (remove duplicate fields)