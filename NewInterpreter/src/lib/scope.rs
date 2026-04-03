use std::collections::HashMap;

use super::variable::{Value, Variable};

#[derive(Debug, Clone)]
pub struct Scope {
    pub vars: HashMap<String, Variable>,
    pub parent: Option<Box<Scope>>,
}

impl Scope {
    pub fn new(parent: Option<Box<Scope>>) -> Self {
        Self {
            vars: HashMap::new(),
            parent,
        }
    }

    // Mengubah Result Error menjadi String agar bisa menampung pesan format!
    pub fn get(&self, attr: &str, get_index: &str) -> Result<&Variable, String> {
        if get_index == "name" {
            if let Some(var) = self.vars.get(attr) {
                return Ok(var);
            }
            if let Some(ref p) = self.parent {
                return p.get(attr, "name");
            }
            Err(format!("Variabel '{}' tidak ditemukan", attr))
        } 
        else if get_index == "address" {
            for var in self.vars.values() {
                if var.address == attr {
                    return Ok(var);
                }
            }
            if let Some(ref p) = self.parent {
                return p.get(attr, "address");
            }
            Err(format!("Memory '{}' tidak ditemukan", attr))
        } 
        else {
            Err(format!("Mode '{}' tidak valid", get_index))
        }
    }

    pub fn set(&mut self, name: &str, value: Value, type_ann: String, mut address: Option<String>) -> Result<(), String> {
        if let Some(var) = self.vars.get_mut(name) {
            if var.constant {
                return Err(format!("Variabel '{}' adalah final", name));
            }
            var.value = value;
            return Ok(());
        }
        
        // Gunakan .is_none() untuk mengecek Option
        if address.is_none() {
            let address_ptr = &value as *const Value; // Cast ke tipe yang benar
            address = Some(format!("{:p}", address_ptr));
        }

        if let Some(ref mut p) = self.parent {
            if p.has(name) {
                // Jangan lupa menambahkan unwrap atau return hasil rekursifnya
                return p.set(name, value, type_ann, address);
            }
        }

        // Jika tidak ada di parent, deklarasikan di scope saat ini
        self.declare(name, value, type_ann, address, false)
    }

    pub fn declare(&mut self, name: &str, value: Value, type_ann: String, mut address: Option<String>, constant: bool) -> Result<(), String> {
        if self.vars.contains_key(name) {
            return Err(format!("Variabel '{}' sudah ada di scope ini", name));
        }
        
        if address.is_none() {
            let address_ptr = &value as *const Value;
            address = Some(format!("{:p}", address_ptr));
        }

        let var = Variable {
            tipe: type_ann,
            value,
            // Gunakan unwrap() karena kita yakin sudah diisi di atas
            address: address.unwrap(), 
            constant,
        };

        self.vars.insert(name.to_string(), var);
        Ok(())
    }

    pub fn has(&self, name: &str) -> bool {
        self.vars.contains_key(name)
    }
}