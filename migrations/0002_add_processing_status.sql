ALTER TABLE `raw_events`
ADD COLUMN `status` ENUM('pending', 'processing', 'done', 'failed') 
    NOT NULL DEFAULT 'pending',
ADD INDEX idx_status (`status`);