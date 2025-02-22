"use client";

import { motion } from "framer-motion";
import React from "react";
import { AuroraBackground } from "./ui/aurora-background";
import { FeaturesSectionDemo } from "./ui/glowing-effect";
import { Link } from "react-router-dom";

export function AuroraBackgroundDemo() {
  return (
    <div className="bg-gray-900">
      <AuroraBackground>
        <motion.div
          initial={{ opacity: 0.0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{
            delay: 0.3,
            duration: 0.8,
            ease: "easeInOut",
          }}
          className="relative flex flex-col gap-4 items-center justify-center px-4"
        >
          <div className="text-3xl md:text-7xl font-bold text-white text-center">
            Edit content like never before
          </div>
          <div className="font-extralight text-base md:text-4xl text-neutral-200 py-4">
            And this, is just the beginning.
          </div>
          <Link to="/feature">
            <button className="bg-white text-black rounded-full w-fit px-4 py-2 hover:bg-gray-100 transition-colors">
              Start now
            </button>
          </Link>
        </motion.div>
      </AuroraBackground>
    </div>
  );
}