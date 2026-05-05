// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use std::collections::HashMap;use crate::incus::MetadataConfigKey;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct MetadataConfigGroup {
    pub keys: Vec<HashMap<String, MetadataConfigKey>>,

}