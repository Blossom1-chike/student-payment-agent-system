"use client"

import { Card } from "@/components/ui/card"
import { BookOpen, Calendar, CreditCard, HelpCircle, GraduationCap, MapPin } from "lucide-react"

const quickActions = [
  {
    icon: CreditCard,
    title: "Payment Help",
    description: "Tuition fees and payment plans",
    color: "text-blue-600 dark:text-blue-400",
    bg: "bg-blue-50 dark:bg-blue-950/30",
  },
  {
    icon: Calendar,
    title: "Book Appointment",
    description: "Schedule meetings with advisors",
    color: "text-purple-600 dark:text-purple-400",
    bg: "bg-purple-50 dark:bg-purple-950/30",
  },
  {
    icon: BookOpen,
    title: "Course Information",
    description: "Modules, timetables, and resources",
    color: "text-green-600 dark:text-green-400",
    bg: "bg-green-50 dark:bg-green-950/30",
  },
  {
    icon: GraduationCap,
    title: "Academic Support",
    description: "Library, tutoring, and study help",
    color: "text-orange-600 dark:text-orange-400",
    bg: "bg-orange-50 dark:bg-orange-950/30",
  },
  {
    icon: MapPin,
    title: "Campus Services",
    description: "Facilities, maps, and locations",
    color: "text-pink-600 dark:text-pink-400",
    bg: "bg-pink-50 dark:bg-pink-950/30",
  },
  {
    icon: HelpCircle,
    title: "General Enquiries",
    description: "Any other questions or concerns",
    color: "text-teal-600 dark:text-teal-400",
    bg: "bg-teal-50 dark:bg-teal-950/30",
  },
]

export function WelcomeScreen() {
  return (
    <div className="space-y-8 py-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="text-center space-y-4">
        <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-primary/10 animate-in zoom-in duration-500">
          <GraduationCap className="h-8 w-8 text-primary" />
        </div>
        <div className="space-y-2">
          <h2 className="text-3xl md:text-4xl font-bold text-balance">Hello! I'm AskNorthumbria</h2>
          <p className="text-lg text-muted-foreground text-pretty max-w-2xl mx-auto">
            Your intelligent assistant for all university queries. I'm here to help with payments, appointments,
            courses, and any questions you have about Northumbria University.
          </p>
        </div>
      </div>

      <div className="space-y-3">
        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wide text-center">
          How can I help you today?
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {quickActions.map((action, index) => (
            <Card
              key={action.title}
              className="p-4 hover:shadow-md transition-all duration-300 cursor-pointer hover:-translate-y-1 group animate-in fade-in slide-in-from-bottom-4"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="flex items-start gap-3">
                <div className={`p-2 rounded-lg ${action.bg} transition-transform group-hover:scale-110`}>
                  <action.icon className={`h-5 w-5 ${action.color}`} />
                </div>
                <div className="flex-1 space-y-1">
                  <h4 className="font-semibold text-sm text-foreground">{action.title}</h4>
                  <p className="text-xs text-muted-foreground">{action.description}</p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      <div className="text-center">
        <p className="text-sm text-muted-foreground">
          💡 <span className="font-medium">Tip:</span> You can type your question below or attach relevant documents
        </p>
      </div>
    </div>
  )
}
