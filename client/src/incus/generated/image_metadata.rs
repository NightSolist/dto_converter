// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use std::collections::HashMap;use crate::incus::ImageMetadataTemplate;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ImageMetadata {
    pub architecture: String,

    pub creationdate: i64,

    pub expirydate: i64,

    pub properties: HashMap<String, String>,

    pub templates: HashMap<String, Option<ImageMetadataTemplate>>,

}