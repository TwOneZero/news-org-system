## ADDED Requirements

### Requirement: Service shall provide overall collection statistics

The system SHALL provide aggregate statistics about news collection.

#### Scenario: Get overall statistics
- **WHEN** collection statistics are requested
- **THEN** the system SHALL return total number of articles collected
- **AND** the system SHALL return number of articles per source
- **AND** the system SHALL return date range of articles (oldest and newest)
- **AND** the system SHALL return timestamp of last successful collection
- **AND** the system SHALL return number of configured feeds

### Requirement: Service shall provide per-source statistics

The system SHALL provide detailed statistics for each configured feed source.

#### Scenario: Get per-source statistics
- **WHEN** statistics are requested for a specific source
- **THEN** the system SHALL return total article count for that source
- **AND** the system SHALL return date of most recent article from that source
- **AND** the system SHALL return date of oldest article from that source
- **AND** the system SHALL return feed URL and adapter information

#### Scenario: Get all sources summary
- **WHEN** statistics are requested for all sources
- **THEN** the system SHALL return an array of statistics for each source
- **AND** each entry SHALL include source name, article count, and date range

### Requirement: Service shall track collection history

The system SHALL maintain a history of collection operations.

#### Scenario: Get recent collection operations
- **WHEN** collection history is requested
- **THEN** the system SHALL return recent collection operations
- **AND** each operation SHALL include timestamp, source, and articles collected count
- **AND** the results SHALL be ordered by timestamp (most recent first)

#### Scenario: Record collection operation
- **WHEN** a collection operation completes
- **THEN** the system SHALL record the operation timestamp
- **AND** the system SHALL record which source was collected
- **AND** the system SHALL record the number of new articles added
- **AND** the system SHALL record success or failure status
