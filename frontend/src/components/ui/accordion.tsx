"use client"

import * as React from "react"
import { ChevronDown } from "lucide-react"

import { cn } from "@/lib/utils"

// Composant Accordion simplifié qui utilise un état local pour gérer l'ouverture/fermeture
interface AccordionProps extends React.HTMLAttributes<HTMLDivElement> {
  type?: "single" | "multiple" | string
  collapsible?: boolean | string
}

const Accordion: React.FC<AccordionProps> = ({ 
  className, 
  children,
  type,
  collapsible,
  ...props 
}) => {
  // Filtrer les props pour ne pas passer type et collapsible au DOM
  return (
    <div className={cn("w-full", className)} {...props}>
      {children}
    </div>
  )
}

// Composant AccordionItem simplifié
interface AccordionItemProps extends React.HTMLAttributes<HTMLDivElement> {
  value?: string
}

const AccordionItem: React.FC<AccordionItemProps> = ({ 
  className, 
  children,
  value,
  ...props 
}) => {
  // Filtrer l'attribut value pour éviter qu'il ne soit passé au DOM
  return (
    <div className={cn("border-b", className)} {...props}>
      {children}
    </div>
  )
}

// Composant AccordionTrigger avec gestion d'état pour l'ouverture/fermeture
interface AccordionTriggerProps extends React.HTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode
  open?: boolean
  onOpenChange?: (open: boolean) => void
}

const AccordionTrigger: React.FC<AccordionTriggerProps> = ({ 
  className, 
  children,
  open: controlledOpen,
  onOpenChange,
  ...props 
}) => {
  // État local pour gérer l'ouverture/fermeture si non contrôlé
  const [uncontrolledOpen, setUncontrolledOpen] = React.useState(false)
  
  // Déterminer si le composant est en mode contrôlé ou non
  const isControlled = controlledOpen !== undefined
  const isOpen = isControlled ? controlledOpen : uncontrolledOpen
  
  // Fonction pour gérer le changement d'état
  const handleToggle = () => {
    if (isControlled) {
      onOpenChange?.(!isOpen)
    } else {
      setUncontrolledOpen(!isOpen)
    }
  }

  return (
    <div className="flex">
      <button
        type="button"
        onClick={handleToggle}
        className={cn(
          "flex flex-1 items-center justify-between py-4 font-medium transition-all hover:underline",
          className
        )}
        data-state={isOpen ? "open" : "closed"}
        {...props}
      >
        {children}
        <ChevronDown 
          className={cn(
            "h-4 w-4 shrink-0 transition-transform duration-200",
            isOpen ? "rotate-180" : ""
          )} 
        />
      </button>
    </div>
  )
}

// Composant AccordionContent simplifié qui utilise l'état du trigger parent
interface AccordionContentProps extends React.HTMLAttributes<HTMLDivElement> {
  open?: boolean
}

const AccordionContent: React.FC<AccordionContentProps> = ({ 
  className, 
  children,
  open = true, // Par défaut, le contenu est visible pour simplifier
  ...props 
}) => {
  return (
    <div
      className={cn(
        "overflow-hidden text-sm",
        className
      )}
      {...props}
    >
      <div className="pb-4 pt-0">{children}</div>
    </div>
  )
}

export { Accordion, AccordionItem, AccordionTrigger, AccordionContent }
