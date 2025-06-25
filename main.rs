\NYX V2

use std::collections::HashMap;

#[derive(Debug, Clone, Copy)]
enum Instruction {
    Load(u8),
    Add(u8),
    Store(u8),
    Jump(u8),
    Halt,
}

struct CPU {
    acc: u8,
    pc: usize,
    memory: [u8; 256],
    program: Vec<Instruction>,
    running: bool,
}

impl CPU {
    fn new(program: Vec<Instruction>) -> Self {
        Self {
            acc: 0,
            pc: 0,
            memory: [0; 256],
            program,
            running: true,
        }
    }

    fn run(&mut self) {
        while self.running {
            if self.pc >= self.program.len() {
                break;
            }

            match self.program[self.pc] {
                Instruction::Load(value) => {
                    self.acc = value;
                    println!("LOAD {}", value);
                }
                Instruction::Add(value) => {
                    self.acc = self.acc.wrapping_add(value);
                    println!("ADD {}", value);
                }
                Instruction::Store(addr) => {
                    self.memory[addr as usize] = self.acc;
                    println!("STORE ACC ({}) to {}", self.acc, addr);
                }
                Instruction::Jump(target) => {
                    println!("JUMP to {}", target);
                    self.pc = target as usize;
                    continue;
                }
                Instruction::Halt => {
                    println!("HALT");
                    self.running = false;
                }
            }

            self.pc += 1;
        }

        println!("\nFinal ACC: {}", self.acc);
        println!("Memory Dump (0..16): {:?}", &self.memory[0..16]);
    }
}

fn main() {
    let program = vec![
        Instruction::Load(5),
        Instruction::Add(10),
        Instruction::Store(0),
        Instruction::Halt,
    ];

    let mut cpu = CPU::new(program);
    cpu.run();
}
