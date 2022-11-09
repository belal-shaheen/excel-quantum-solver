import * as React from "react";
import { DefaultButton, Label, Dropdown, TextField } from "@fluentui/react";
import Header from "./Header";
import HeroList, { HeroListItem } from "./HeroList";
import Progress from "./Progress";
import { ChoiceGroup, IChoiceGroupOption } from "@fluentui/react/lib/ChoiceGroup";
import { parse, visit } from "excel-formula-parser";
import { Node, NumberNode } from "excel-formula-ast";
/* global console, Excel, require  */

export interface AppProps {
  title: string;
  isOfficeInitialized: boolean;
}

const options: IChoiceGroupOption[] = [
  { key: "max", text: "Max" },
  { key: "min", text: "Min" },
  { key: "value", text: "Value of" },
];

function isNumeric(str) {
  if (typeof str != "string") return false; // we only process strings!
  return (
    // @ts-ignore
    !isNaN(str) && // use type coercion to parse the _entirety_ of the string (`parseFloat` alone does not do this)...
    !isNaN(parseFloat(str))
  ); // ...and ensure strings of whitespace fail
}

const App = ({}: AppProps) => {
  const [objective, setObjective] = React.useState<string>("$E$4");
  const [objectiveTarget, setObjectiveTarget] = React.useState<string>("max");
  const [objectiveValue, setObjectiveValue] = React.useState<number>(0);
  const [rawVariableCells, setRawVariableCells] = React.useState<string>("$C$3:$D$3");
  const [variableCells, setVariableCells] = React.useState<Array<string>>([]);
  const [rawConstraints, setRawConstraints] = React.useState<string>("$E$7 <= $F$7 \n$E$8 <= $F$8 \n$E$9 <= $F$9");
  const [constraints, setConstraints] = React.useState<Array<any>>([]);
  const [objectiveFormula, setObjectiveFormula] = React.useState<any>([]);
  const [solution, setSolution] = React.useState<any>({});

  const parseTheFormulaTree = async (context: Excel.RequestContext, sheet: Excel.Worksheet, node: Node) => {
    switch (node.type) {
      case "binary-expression":
        await parseTheFormulaTree(context, sheet, node.left);
        await parseTheFormulaTree(context, sheet, node.right);
        break;
      case "cell":
        const range = sheet.getRange(node.key);
        range.load("formulas");
        await context.sync();
        const rawFormula = range.formulas[0][0];
        const includesAVariableKey = variableCells.includes(node.key);
        if (!includesAVariableKey) {
          if (isNumeric(rawFormula) || typeof rawFormula === "number") {
            // @ts-ignore
            node.value = rawFormula.toString();
            // @ts-ignore
            node.type = "number";
          } else {
            const parsedFormula = parse(rawFormula);
            await parseTheFormulaTree(context, sheet, parsedFormula);
            if (parsedFormula.type === "binary-expression") {
              // @ts-ignore
              node.left = parsedFormula.left;
              // @ts-ignore
              node.right = parsedFormula.right;
              // @ts-ignore
              node.operator = parsedFormula.operator;
              // @ts-ignore
              node.type = "binary-expression";
            }
          }
        }
    }
    await context.sync();
  };

  const generateSolverFormulas = () => {
    Excel.run(async (context) => {
      const sheet = context.workbook.worksheets.getActiveWorksheet();
      const objectiveRange = sheet.getRange(objective);
      objectiveRange.load("formulas");

      const variableRange = sheet.getRange(rawVariableCells);
      variableRange.format.fill.color = "green";
      variableRange.load(["rowCount", "columnCount", "cellCount"]);
      const propertiesToGet = variableRange.getCellProperties({
        address: true,
      });

      await context.sync();

      var arrAddress = [];
      for (let iRow = 0; iRow < variableRange.rowCount; iRow++) {
        for (let iCol = 0; iCol < variableRange.columnCount; iCol++) {
          const cellAddress = propertiesToGet.value[iRow][iCol];
          arrAddress.push(cellAddress.address.slice(cellAddress.address.lastIndexOf("!") + 1));
        }
      }
      setVariableCells(arrAddress);

      const rawFormula = objectiveRange.formulas[0][0];
      const parsedFormula = parse(rawFormula);
      await parseTheFormulaTree(context, sheet, parsedFormula);
      setObjectiveFormula(parsedFormula);

      const editedConstraints = rawConstraints.split("\n");
      const constraints = [];
      for (let i = 0; i < editedConstraints.length; i++) {
        const constraint = editedConstraints[i];
        const parsedConstraint = parse(constraint);
        await parseTheFormulaTree(context, sheet, parsedConstraint);
        constraints.push(parsedConstraint);
      }
      setConstraints(constraints);
    }).catch((error) => {
      console.log(error);
      if (error instanceof OfficeExtension.Error) {
        console.log("Debug info: " + JSON.stringify(error.debugInfo));
      }
    });
  };

  const request = async () => {
    const url = "https://localhost:8000/api/solve";
    let xhttp = new XMLHttpRequest();
    return new Promise(function (resolve, reject) {
      xhttp.onreadystatechange = function () {
        if (xhttp.readyState !== 4) return;

        if (xhttp.status == 200) {
          resolve(JSON.parse(xhttp.responseText));
        } else {
          reject({
            status: xhttp.status,

            statusText: xhttp.statusText,
          });
        }
      };
      xhttp.open("POST", url, true);
      xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
      xhttp.send(
        JSON.stringify({
          variableCells: variableCells,
          constraints: constraints,
          objectiveTarget: objectiveTarget,
          objectiveFormula: objectiveFormula,
        })
      );
    });
  };

  const solve = async () => {
    await generateSolverFormulas();
    const response: Object = await request();
    setSolution(response);
    await Excel.run(async (context) => {
      const sheet = context.workbook.worksheets.getActiveWorksheet();
      for (var key in response) {
        if (response.hasOwnProperty(key)) {
          let range = sheet.getRange(key as string);
          range.values = [[response[key]]];
          await context.sync();
        }
      }
    });
    // setStuff(response.toString());
  };

  return (
    <div>
      {/* Ask for objective */}
      <Label>Set Objective:</Label>
      <TextField onChange={(_, v) => setObjective(v)} value={objective} placeholder="$a$1" type="text" id="objective" />
      <Label>To:</Label>
      {/* Select between options: Max, Min, Value of */}
      <ChoiceGroup
        title="objective-target"
        onChange={(_, option) => setObjectiveTarget(option.key)}
        value={objectiveTarget}
        options={options}
      />
      <TextField
        onChange={(_, v) => setObjectiveValue(parseInt(v))}
        value={objectiveValue.toString()}
        placeholder="0"
        disabled={objectiveTarget !== "value"}
        type="number"
        id="objectiveValue"
      />
      <Label>By Changing Variable Cells:</Label>
      <TextField
        title="variable-cells"
        type="text"
        id="variableCells"
        placeholder="$a$1:$a$10"
        onChange={(_, v) => setRawVariableCells(v)}
        value={rawVariableCells}
      />
      <Label>Subject to the Constraints:</Label>
      <TextField
        onChange={(_, v) => setRawConstraints(v)}
        value={rawConstraints}
        multiline
        title="constraints"
        id="constraints"
        placeholder="A1 &gt; 0"
      />
      <br />
      <DefaultButton onClick={solve}>Solve</DefaultButton>
    </div>
  );
};

export default App;
