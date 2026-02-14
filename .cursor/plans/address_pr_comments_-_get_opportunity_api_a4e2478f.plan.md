---
name: Address PR Comments - GET Opportunity API
overview: "Refactor GET Opportunity API to address 4 PR comments: use DTO instead of entity, constructor injection with Lombok, add @Transactional, and switch to JpaRepository."
todos:
  - id: create-dto
    content: Create OpportunityDTO with all entity fields
    status: completed
  - id: create-mapper
    content: Create OpportunityMapper utility class
    status: completed
  - id: update-repo
    content: Change OpportunityRepository to extend JpaRepository
    status: completed
  - id: update-service-interface
    content: Update OpportunityService return type to DTO
    status: completed
  - id: update-service-impl
    content: Add constructor injection, @Transactional, DTO mapping in OpportunityServiceImpl
    status: completed
  - id: update-controller
    content: Add constructor injection, update return type to DTO in OpportunityController
    status: completed
  - id: update-tests
    content: Update both test files for DTO assertions
    status: completed
  - id: verify
    content: Run tests and verify all pass
    status: completed
---

# Address PR Comments - GET Opportunity API Refactoring

## Changes Overview

Address 4 PR review comments by implementing DTOs, constructor injection, transactions, and JpaRepository.

## Implementation Steps

### 1. Create OpportunityDTO

Create [`src/main/java/com/adobe/dealtracker/dto/OpportunityDTO.java`](src/main/java/com/adobe/dealtracker/dto/OpportunityDTO.java):
- All fields from Opportunity entity (including audit fields)
- Use Lombok `@Getter`, `@Setter`, `@Builder`, `@AllArgsConstructor`, `@NoArgsConstructor`
- Matches API schema response structure
- No JPA annotations

### 2. Create OpportunityMapper

Create [`src/main/java/com/adobe/dealtracker/mapper/OpportunityMapper.java`](src/main/java/com/adobe/dealtracker/mapper/OpportunityMapper.java):
- Utility class with static method `toDTO(Opportunity entity)`
- Field-by-field mapping from entity to DTO
- Handle null safety

### 3. Update OpportunityRepository

Modify [`src/main/java/com/adobe/dealtracker/repository/OpportunityRepository.java`](src/main/java/com/adobe/dealtracker/repository/OpportunityRepository.java):
- Change from `CrudRepository` to `JpaRepository`
- Keep generic types `<Opportunity, String>`

### 4. Update OpportunityService Interface

Modify [`src/main/java/com/adobe/dealtracker/service/OpportunityService.java`](src/main/java/com/adobe/dealtracker/service/OpportunityService.java):
- Change return type from `Optional<Opportunity>` to `Optional<OpportunityDTO>`

### 5. Update OpportunityServiceImpl

Modify [`src/main/java/com/adobe/dealtracker/service/impl/OpportunityServiceImpl.java`](src/main/java/com/adobe/dealtracker/service/impl/OpportunityServiceImpl.java):
- Add `@RequiredArgsConstructor` (Lombok)
- Change field to `private final OpportunityRepository`
- Remove `@Autowired` annotation
- Add `@Transactional(readOnly = true)` to method
- Map entity to DTO using OpportunityMapper
- Update return type to `Optional<OpportunityDTO>`

### 6. Update OpportunityController

Modify [`src/main/java/com/adobe/dealtracker/resource/OpportunityController.java`](src/main/java/com/adobe/dealtracker/resource/OpportunityController.java):
- Add `@RequiredArgsConstructor` (Lombok)
- Change field to `private final OpportunityService`
- Remove `@Autowired` annotation
- Update return type to `ResponseEntity<OpportunityDTO>`
- Update Swagger `@ApiResponse` schema from `Opportunity.class` to `OpportunityDTO.class`

### 7. Update OpportunityServiceImplTest

Modify [`src/test/java/com/adobe/dealtracker/service/impl/OpportunityServiceImplTest.java`](src/test/java/com/adobe/dealtracker/service/impl/OpportunityServiceImplTest.java):
- Update assertions to check DTO fields instead of entity
- Verify mapper is called correctly
- Update mock return types

### 8. Update OpportunityControllerTest

Modify [`src/test/java/com/adobe/dealtracker/resource/OpportunityControllerTest.java`](src/test/java/com/adobe/dealtracker/resource/OpportunityControllerTest.java):
- Update service mock to return `Optional<OpportunityDTO>`
- Update JSON response assertions to match DTO structure
- Verify all DTO fields in response

## Testing Verification

After changes:
1. Run unit tests: `./mvnw test`
2. Verify all tests pass
3. Check API response returns DTO with all fields

## Files Changed

- **New**: `dto/OpportunityDTO.java`, `mapper/OpportunityMapper.java`
- **Modified**: `OpportunityRepository.java`, `OpportunityService.java`, `OpportunityServiceImpl.java`, `OpportunityController.java`, test files