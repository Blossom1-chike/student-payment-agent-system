"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Camera, X, RotateCcw, Send } from "lucide-react"

interface IdCameraCaptureProps {
  onCapture: (imageBlob: Blob) => void
  onClose: () => void
}

export function IdCameraCapture({ onCapture, onClose }: IdCameraCaptureProps) {
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [capturedImage, setCapturedImage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    startCamera()
    return () => {
      stopCamera()
    }
  }, [])

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user", width: 1280, height: 720 },
        audio: false,
      })
      setStream(mediaStream)
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
    } catch (err) {
      setError("Unable to access camera. Please check your permissions.")
      console.error("Camera error:", err)
    }
  }

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop())
      setStream(null)
    }
  }

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current
      const canvas = canvasRef.current
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      const ctx = canvas.getContext("2d")
      if (ctx) {
        ctx.drawImage(video, 0, 0)
        const imageDataUrl = canvas.toDataURL("image/jpeg", 0.9)
        console.log("Captured image data URL:", imageDataUrl)
        setCapturedImage(imageDataUrl)
        stopCamera()
      }
    }
  }

  const retakePhoto = () => {
    setCapturedImage(null)
    startCamera()
  }

  const sendPhoto = () => {
    if (capturedImage && canvasRef.current) {
      canvasRef.current.toBlob(
        (blob) => {
          if (blob) {
            onCapture(blob)
            onClose()
          }
        },
        "image/jpeg",
        0.9,
      )
    }
  }

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in">
      <Card className="w-full max-w-2xl bg-card shadow-2xl overflow-hidden animate-in zoom-in-95 slide-in-from-bottom-4">
        {/* Header */}
        <div className="border-b bg-card/50 backdrop-blur-sm p-4 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-foreground">ID Verification</h2>
            <p className="text-sm text-muted-foreground">Please hold your ID card next to your face</p>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8">
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Camera/Preview Area */}
        <div className="relative bg-black aspect-video">
          {error ? (
            <div className="absolute inset-0 flex items-center justify-center p-8">
              <div className="text-center">
                <Camera className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-white mb-4">{error}</p>
                <Button onClick={startCamera} variant="secondary">
                  Try Again
                </Button>
              </div>
            </div>
          ) : capturedImage ? (
            <img src={capturedImage || "/placeholder.svg"} alt="Captured ID" className="w-full h-full object-contain" />
          ) : (
            <>
              <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover mirror" />
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="border-4 border-primary/60 rounded-2xl w-[80%] h-[80%] relative animate-pulse">
                  <div className="absolute -top-1 -left-1 w-8 h-8 border-t-4 border-l-4 border-primary rounded-tl-lg" />
                  <div className="absolute -top-1 -right-1 w-8 h-8 border-t-4 border-r-4 border-primary rounded-tr-lg" />
                  <div className="absolute -bottom-1 -left-1 w-8 h-8 border-b-4 border-l-4 border-primary rounded-bl-lg" />
                  <div className="absolute -bottom-1 -right-1 w-8 h-8 border-b-4 border-r-4 border-primary rounded-br-lg" />
                </div>
              </div>
              <div className="absolute top-4 left-1/2 -translate-x-1/2 bg-black/60 backdrop-blur-sm text-white px-4 py-2 rounded-full text-sm">
                Position your face and ID within the frame
              </div>
            </>
          )}
          <canvas ref={canvasRef} className="hidden" />
        </div>

        {/* Controls */}
        <div className="p-4 bg-card/50 backdrop-blur-sm border-t">
          {capturedImage ? (
            <div className="flex gap-3 justify-center">
              <Button onClick={retakePhoto} variant="outline" className="gap-2 bg-transparent">
                <RotateCcw className="h-4 w-4" />
                Retake
              </Button>
              <Button onClick={sendPhoto} className="gap-2 bg-primary hover:bg-primary/90">
                <Send className="h-4 w-4" />
                Send to Verify
              </Button>
            </div>
          ) : (
            <Button onClick={capturePhoto} disabled={!stream} className="w-full gap-2 bg-primary hover:bg-primary/90">
              <Camera className="h-5 w-5" />
              Capture Photo
            </Button>
          )}
          <p className="text-xs text-center text-muted-foreground mt-3">
            Make sure your face and ID card are clearly visible
          </p>
        </div>
      </Card>
    </div>
  )
}
