// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use std::collections::HashMap;
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct EventLogging {
    pub message: String,

    pub level: String,

    pub context: HashMap<String, String>,

}