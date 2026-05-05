// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use std::collections::HashMap;
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ImagePut {
    pub autoupdate: bool,

    pub properties: HashMap<String, String>,

    pub public: bool,

    pub expiresat: chrono::DateTime<chrono::Utc>,

    pub profiles: Vec<String>,

}