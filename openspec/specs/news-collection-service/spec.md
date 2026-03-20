## ADDED Requirements

### Requirement: Service shall collect articles from configured RSS feeds

The system SHALL provide a service that collects articles from all configured RSS feeds.

#### Scenario: Successful collection from all feeds
- **WHEN** the collection service is invoked
- **THEN** the system SHALL iterate through all configured feeds in the registry
- **AND** the system SHALL use the appropriate adapter for each feed
- **AND** the system SHALL parse and store articles from each feed
- **AND** the system SHALL return a summary of articles collected per feed

#### Scenario: Collection with feed-specific failures
- **WHEN** one or more feeds fail to parse
- **THEN** the system SHALL continue processing remaining feeds
- **AND** the system SHALL report which feeds succeeded and which failed
- **AND** the system SHALL include error details for failed feeds

### Requirement: Service shall collect articles from specific feed

The system SHALL provide a service that collects articles from a single specified feed.

#### Scenario: Successful collection from specific feed
- **WHEN** the collection service is invoked with a specific feed name
- **THEN** the system SHALL fetch articles only from the specified feed
- **AND** the system SHALL use the appropriate adapter for that feed
- **AND** the system SHALL return the count of articles collected

#### Scenario: Collection from non-existent feed
- **WHEN** the collection service is invoked with an unknown feed name
- **THEN** the system SHALL return an error
- **AND** the system SHALL indicate the feed was not found in the registry

### Requirement: Service shall support incremental collection

The system SHALL support collecting only new articles since the last collection.

#### Scenario: Incremental collection
- **WHEN** the collection service is invoked with incremental mode
- **THEN** the system SHALL use URL-based deduplication to skip existing articles
- **AND** the system SHALL only store articles not already in the database
- **AND** the system SHALL report the number of new articles added

### Requirement: Service shall provide collection status

The system SHALL provide information about collection operations.

#### Scenario: Get collection statistics
- **WHEN** the collection service is queried for statistics
- **THEN** the system SHALL return total article count
- **AND** the system SHALL return article count per feed/source
- **AND** the system SHALL return timestamp of last successful collection
