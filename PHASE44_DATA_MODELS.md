# PHASE 44 — SECURITY MARKETPLACE DATA MODELS

## 1. Database Entities

1. **`MarketplacePackage` (`marketplace_packages`)**:
   - `id`, `tenant_id`, `package_name`, `package_type`, `version`, `author`, `verified_publisher`, `signature_hash`, `installs_count`, `status`, `created_at`.
2. **`InstalledExtension` (`installed_extensions`)**:
   - `id`, `tenant_id`, `package_id`, `package_name`, `installed_version`, `auto_update`, `enabled`, `installed_at`.
3. **`PackageReviewRating` (`package_review_ratings`)**:
   - `id`, `tenant_id`, `package_id`, `reviewer_name`, `rating_stars`, `review_comment`, `submitted_at`.
