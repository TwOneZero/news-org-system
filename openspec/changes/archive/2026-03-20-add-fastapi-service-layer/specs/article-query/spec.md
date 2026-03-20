## ADDED Requirements

### Requirement: Service shall support querying articles with filters

The system SHALL provide a service to query articles with various filter criteria.

#### Scenario: Query all articles
- **WHEN** articles are queried without filters
- **THEN** the system SHALL return all articles in the database
- **AND** the results SHALL be ordered by publication date (newest first)

#### Scenario: Query by source
- **WHEN** articles are queried with a specific source name filter
- **THEN** the system SHALL return only articles from that source
- **AND** the results SHALL be ordered by publication date (newest first)

#### Scenario: Query by date range
- **WHEN** articles are queried with start and end date parameters
- **THEN** the system SHALL return only articles published within the date range
- **AND** the results SHALL be ordered by publication date (newest first)

#### Scenario: Query by keyword
- **WHEN** articles are queried with a keyword search parameter
- **THEN** the system SHALL return articles where the keyword appears in title or content
- **AND** the search SHALL be case-insensitive

#### Scenario: Combined filters
- **WHEN** articles are queried with multiple filters (source, date range, keyword)
- **THEN** the system SHALL return articles matching ALL specified filters
- **AND** the results SHALL be ordered by publication date (newest first)

### Requirement: Service shall support pagination

The system SHALL support pagination for article query results.

#### Scenario: Paginate results
- **WHEN** articles are queried with page and page_size parameters
- **THEN** the system SHALL return the specified page of results
- **AND** the system SHALL return total count of matching articles
- **AND** the system SHALL return total page count
- **AND** each page SHALL contain at most `page_size` articles

#### Scenario: Default pagination
- **WHEN** articles are queried without pagination parameters
- **THEN** the system SHALL use default page size of 20
- **AND** the system SHALL return the first page

#### Scenario: Invalid pagination
- **WHEN** articles are queried with page size greater than maximum
- **THEN** the system SHALL use the maximum page size
- **AND** the system SHALL return a warning in the response

### Requirement: Service shall support retrieving single article

The system SHALL provide a method to retrieve a single article by ID.

#### Scenario: Retrieve existing article
- **WHEN** an article is requested by its ID
- **THEN** the system SHALL return the complete article data
- **AND** the response SHALL include all article fields

#### Scenario: Retrieve non-existent article
- **WHEN** an article is requested with an ID that does not exist
- **THEN** the system SHALL return a not found error
