// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use std::collections::HashMap;use crate::incus::ProjectStateResource;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ProjectState {
    pub resources: HashMap<String, ProjectStateResource>,

}