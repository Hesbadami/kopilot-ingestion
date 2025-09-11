CREATE TABLE IF NOT EXISTS `raw_events` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `timestamp` DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
    `source` ENUM('telegram', 'zoom', 'airtable', 'ghl') NOT NULL,
    `payload` JSON NOT NULL,
    `processed` BOOLEAN DEFAULT FALSE,
    `processed_at` DATETIME(6) NULL,
    `error_message` TEXT NULL,
    `retry_count` INT UNSIGNED DEFAULT 0,

    INDEX `idx_source_timestamp` (`source`, `timestamp`),
    INDEX `idx_processed` (`processed`),
    INDEX `idx_source` (`source`)
)