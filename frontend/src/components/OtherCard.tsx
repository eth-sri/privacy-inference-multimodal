import * as React from "react"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"

import { selectList } from "@/types/selectList"
import { ChangeEvent } from "react"
import { Textarea } from "./ui/textarea"

interface Props {
  name: string,
  description: string
  type: string,
  select?: selectList[],
  onChange: (name:string, value: any) => void,
  value: any
}

export function CardWithForm({ name, description, select, type, onChange, value }: Props) {

  const handleInputChange = (name:string, event: ChangeEvent<HTMLInputElement|HTMLSelectElement>) => {
    onChange(name, event.target.value);
  };

  const handleSelectChange = (name: string, value: any) => {
    onChange(name, value);
  };

  const handleRadioChange = (name:string, value: any) => {
    onChange(name, value);
  };

  return (
    <Card className="w-full grid grid-cols-5 mb-2">
      <CardHeader>
        <CardTitle><Input></Input></CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent className="col-span-4">
          <div className="grid grid-cols-4 w-full items-center gap-2">
            <div className="flex flex-col">
              {(type === 'text') && <Input id={name+"_input"} value={value.estimate} onChange={(event) => handleInputChange('estimate', event)} placeholder={name} />
              }
              {(type === 'select') && select &&
                <Select value={value.estimate} onValueChange={(value) => handleSelectChange('estimate', value)}>
                  <SelectTrigger id={name+"framework"}>
                    <SelectValue placeholder={"Select "+name} />
                  </SelectTrigger>
                  
                  <SelectContent position="popper">
                    {select.map((select,id) => <SelectItem key={id} value={select.label}>{select.label}</SelectItem>)}
                  </SelectContent>
                </Select>
              }
              {(type === 'radio') && (select) &&
              <RadioGroup className="flex" defaultValue="" value={value.estimate} onValueChange={(value) => handleRadioChange('estimate', value)}>
                {select.map((select,id) => 
                  <div key={id} className="flex items-center space-x-0.5">
                  <RadioGroupItem value={select.label} id={select.value} />
                  <Label htmlFor={select.value}>{select.label}</Label>
                </div>
                )}
            </RadioGroup>
              }
              {(type === 'textarea') && <Textarea placeholder="Other Attributes"></Textarea>
              }
              </div>
              <div className="flex flex-col items-center">
              <Select value={value.hardness === 0 ? '' : value.hardness.toString()} onValueChange={(value) => handleSelectChange('hardness', Number(value))}>
                <SelectTrigger className="m-1" id="hardness">
                  <SelectValue placeholder={"Select Hardness"} />
                </SelectTrigger>
                
                <SelectContent position="popper">
                  <SelectItem value="1">1</SelectItem>
                  <SelectItem value="2">2</SelectItem>
                  <SelectItem value="3">3</SelectItem>
                  <SelectItem value="4">4</SelectItem>
                  <SelectItem value="5">5</SelectItem>
                </SelectContent>
              </Select>
              </div>
              <div className="flex flex-col items-center">
              <Select value={value.certainty===0 ? '' : value.certainty.toString()} onValueChange={(value) => handleSelectChange('certainty', Number(value))}>
                <SelectTrigger className="m-1" id="certainty">
                  <SelectValue placeholder={"Select Certainty"} />
                </SelectTrigger>
                
                <SelectContent position="popper">
                  <SelectItem value="1">1</SelectItem>
                  <SelectItem value="2">2</SelectItem>
                  <SelectItem value="3">3</SelectItem>
                  <SelectItem value="4">4</SelectItem>
                  <SelectItem value="5">5</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex flex-col items-center">
              <Select value={value.information_level===0 ? '' : value.information_level.toString()} onValueChange={(value) => handleSelectChange('information_level', Number(value))}>
                <SelectTrigger className="m-1" id="information_level">
                  <SelectValue placeholder={"Select Information Level"} />
                </SelectTrigger>
                
                <SelectContent position="popper">
                  <SelectItem value="1">Post Information</SelectItem>
                  <SelectItem value="2">+ Post Comments</SelectItem>
                  <SelectItem value="3">+ Author Profile</SelectItem>
                </SelectContent>
              </Select>
            </div>
            {/* <div className="flex flex-col m-2">
              <div className="flex items-center space-x-2">
                <Checkbox id={name+"_checkbox"} />
                <Label htmlFor={name+"_checkbox"}>
                  More Information
                </Label>
              </div>
            </div> */}
          </div>
      </CardContent>
    </Card>
  )
}
