"use client"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Shield } from "lucide-react"

interface PrivacyPolicyModalProps {
  onAccept: () => void
  onReject: () => void
}

export function PrivacyPolicyModal({ onAccept, onReject }: PrivacyPolicyModalProps) {
  return (
    <div className="fixed inset-0 z-50 bg-background/10 backdrop-blur-sm animate-in fade-in">
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Card className="max-w-2xl w-full shadow-2xl border-2 animate-in zoom-in-95 slide-in-from-bottom-4">
          <div className="p-6 space-y-4">
            {/* Header */}
            <div className="flex items-start gap-4">
              <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                <Shield className="h-6 w-6 text-primary" />
              </div>
              <div className="flex-1">
                <h2 className="text-2xl font-semibold text-foreground">Privacy & Data Policy</h2>
                <p className="text-sm text-muted-foreground mt-1">Please review our privacy policy before continuing</p>
              </div>
            </div>

            {/* Policy Content */}
            <ScrollArea className="h-[300px] rounded-lg border bg-accent/50 p-4">
              <div className="space-y-4 text-sm text-foreground leading-relaxed">
                <p className="font-medium text-base">Welcome to AskNorthumbria</p>

                <div>
                  <h3 className="font-semibold mb-2">Information We Collect</h3>
                  <p className="text-muted-foreground">
                    When you use AskNorthumbria, we may collect information about your queries, conversations, and any
                    files you upload to provide you with better assistance. This helps us improve our service and
                    provide accurate responses to your questions about payments, appointments, courses, and university
                    enquiries.
                  </p>
                </div>

                <div>
                  <h3 className="font-semibold mb-2">How We Use Your Data</h3>
                  <p className="text-muted-foreground">
                    Your information is used solely to provide student support services and improve the AskNorthumbria
                    experience. We process your queries to give you relevant information about Northumbria University
                    services, policies, and procedures.
                  </p>
                </div>

                <div>
                  <h3 className="font-semibold mb-2">Data Security</h3>
                  <p className="text-muted-foreground">
                    We implement appropriate security measures to protect your personal information. Your conversations
                    are encrypted and stored securely in compliance with GDPR and UK data protection regulations.
                  </p>
                </div>

                <div>
                  <h3 className="font-semibold mb-2">Your Rights</h3>
                  <p className="text-muted-foreground">
                    You have the right to access, correct, or delete your personal data at any time. You can also
                    withdraw consent for data processing by contacting Northumbria University's data protection officer.
                  </p>
                </div>

                <div>
                  <h3 className="font-semibold mb-2">Cookies and Tracking</h3>
                  <p className="text-muted-foreground">
                    We use essential cookies to maintain your session and remember your preferences. No third-party
                    tracking cookies are used without your explicit consent.
                  </p>
                </div>

                <p className="text-xs text-muted-foreground pt-2 border-t">Last updated: December 2024</p>
              </div>
            </ScrollArea>

            {/* Actions */}
            <div className="flex flex-col sm:flex-row gap-3 pt-2">
              <Button
                onClick={onReject}
                variant="outline"
                className="flex-1 h-11 hover:bg-destructive/10 hover:text-destructive hover:border-destructive/50 transition-colors bg-transparent"
              >
                Reject
              </Button>
              <Button
                onClick={onAccept}
                className="flex-1 h-11 bg-primary hover:bg-primary/90 transition-all hover:scale-[1.02]"
              >
                Accept & Continue
              </Button>
            </div>

            <p className="text-xs text-center text-muted-foreground">
              By accepting, you agree to our privacy policy and terms of service
            </p>
          </div>
        </Card>
      </div>
    </div>
  )
}
