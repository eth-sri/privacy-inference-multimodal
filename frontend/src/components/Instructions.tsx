import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

export function Instructions() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button>Instructions</Button>
      </DialogTrigger>
      <DialogContent className="min-w-[90%]">
        <DialogHeader>
          <DialogTitle>Are you sure absolutely sure?</DialogTitle>
          <DialogDescription className=""></DialogDescription>
        </DialogHeader>
      </DialogContent>
    </Dialog>
  );
}
