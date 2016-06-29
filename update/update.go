package main

import (
    "fmt"
    "log"
    "os/exec"
)

func main() (
    out, err := exec.Command("docker").Output()
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("%s\n", out)
)