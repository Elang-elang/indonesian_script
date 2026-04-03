/* use lalrpop_util::lalrpop_mod;

// Ini akan mencari src/grammar.lalrpop
lalrpop_mod!(pub grammar); 
 */

mod lib;
mod grammar;

fn main() {
    // Inisialisasi parser untuk rule 'Program'
    let parser = grammar::ProgramParser::new();

    let input = r#"
        var<kamus> dict = {};
        final<kamus> kamusan = {
            nama: "elang",
            "umur": 16,
        };
        {
            final<daftar> daftaran = [
                ["nama", "elang"], ["umur", 16]
            ];
        }
    "#;

    // Proses penguraian
    match parser.parse(input) {
        Ok(ast) => {
            println!("Parsing Berhasil!");
            println!("Struktur AST:");
            println!("{:#?}", ast);
        }
        Err(e) => {
            eprintln!("Parsing Gagal!");
            eprintln!("Error: {:?}", e);
        }
    }
}
