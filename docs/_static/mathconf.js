MathJax.Hub.Config({
    TeX: {
        Macros: {
            // Math notation
            Z: "\\mathbb{Z}",                                    // set of integers
            // MoA notations
            minus: "{}^{\\boldsymbol{\\mbox{-}}\\!}",            // scalar negation operator
            rop: ["\\,\\mathrm{#1}^*\\,", 1],                    // relational operation
            op: ["\\,\\mathrm{#1}\\,}", 1],                      // binary operations
            uop: ["\\mathrm{#1}\\,", 1],                         // unary operation
            hop: ["{{}_{#1}\\!\\Omega_{#2}}\\,", 2],             // higher order operation
            id: ["\\mathrm{id}(\\op{#1})", 1],                   // identity of operations
            dims: "\\delta\\,",                                  // array dimension operator
            shape: "\\rho\\,",                                   // array shape operator
            size: "\\tau\\,",                                    // array size operator
            reshape: "\\,\\widehat{\\rho}\\,",                   // reshape operator
            drop: "\\,\\nabla\\,",                               // drop operator
            take: "\\,\\Delta\\,",                               // take operator
            product: "\\pi\\,",                                  // product operator
            // DeclareMathOperator{\\rav}{rav}
            ravel: "\\rav\\,",                                   // ravel operator
            range: "\\iota\\,",                                  // range operator
            transpose: "\\bigcirc\\!\\!\\!\\!\\!\\backslash\\;", // transpose operator, need a better symbol
            vc: ["<#1>", 1],                                     // vector with one component
            vcc: ["<#1\\;#2>", 2],                               // vector with two components
            vccc: ["<#1\\;#2\\;#3>", 3],                         // vector with three components
            vcccc: ["<#1\\;#2\\;#3\\;#4>", 4],                   // vector with four components
            ac: ["[\\;#1\\;]", 1],                               // array with one components
            acc: ["[\\;#1\\;#2\\;>", 2],                         // array with two components
            accc: ["[\\;#1\\;#2\\;#3\\;]", 3],                   // array with three components
            acccc: ["[\\;#1\\;#2\\;#3\\;#4\\;]", 4],             // array with four components
            avcc: ["[\\;<#1>\\;<#2>\\;]", 2],                    // three dimensionar array with two components
            aacc: ["[\\;[\\;#1\\;]\\;[\\;#2\\;]\\;]", 2],        // four dimensionar array with two components
            aaccIcc: ["[\\;[\\;#1\\;#2\\;]\\;[\\;#3\\;#4\\;]\\;]", 4],        // four dimensionar array with two components
            outerprod: ["\\,\\bullet_{#1}\\,", 1],               // outer product opetation
            innerprod: ["\\,{}_{#1}\\!\\!\\bullet_{#2}\\,", 2],  // inner product opetation
            // DeclareMathOperator{\\red}{red}
            reduce: ["{}_{#1}\\!\\red\\,", 1],                   // reduce operator
            getitem: ["{#2}\\,\\psi\\,{#1}", 2],                 // psi operator

            scan: ["{}_{\\op{#1}\\!}\\mathrm{scan}\\,", 1],
            kron: "\\bigcirc\\,\\!\\!\\!\\!\\!\\!\\times\\;",
            cat: "+\\!\\!\\!+",
            gu: "\\mathrm{gu}\\,",
            gd: "\\mathrm{gd}\\,",
            compress: "\\,\\notslash\\,",
            expand: "\\,\\notbackslash\\,",
            reverse: "\\phi\\,",
            rotate: ["{#1}\\theta\\,", 1]
        }
    }
});
