@app.post("/api/validation-loop")
async def enhanced_validation_loop(request: Dict[str, Any]):
    """Progressive validation - ALL 47 rules each time, claim improves to pass MORE rules"""
    try:
        claim_packet = ClaimPacket(**request.get("claim_packet", {}))
        max_iterations = 4
        
        validation_history = []
        previous_scores = []
        iteration = 0
        
        print(f"🚀 Starting Progressive Validation Loop for claim {claim_packet.claim_id}")
        print(f"🎯 Same 47 rules each iteration - claim improves to pass more!")
        
        while iteration < max_iterations:
            iteration += 1
            
            print(f"\n{'='*60}")
            print(f"🔄 ITERATION {iteration}/{max_iterations}")
            print(f"{'='*60}")
            
            # ENHANCE THE CLAIM (so it passes more rules)
            original_doc_count = len(claim_packet.documents)
            
            if iteration == 2:
                print("💳 ITERATION 2: Adding Knot receipts to pass more rules...")
                claim_packet = await auto_enhance_with_knot_receipts(claim_packet)
                print(f"📄 Documents: {original_doc_count} → {len(claim_packet.documents)}")
                
            elif iteration == 3:
                print("🔍 ITERATION 3: Reprocessing documents for better quality...")
                claim_packet = await deep_reprocess_documents(claim_packet)
                
            elif iteration == 4:
                print("⚖️ ITERATION 4: Final review with all enhancements...")
            
            # EVALUATE AGAINST ALL 47 RULES (same rules, better claim)
            validation = await ai_judge.evaluate_with_depth(claim_packet, iteration, previous_scores)
            
            current_score = validation.overall_score
            rules_passed = len([r for r in validation.rules_evaluated if r.passed])
            total_rules = len(validation.rules_evaluated)
            
            print(f"📊 Rules: {rules_passed}/{total_rules} passed = {current_score:.1%}")
            
            # Record results
            validation_history.append({
                "iteration": iteration,
                "analysis_depth": ai_judge._get_depth_name(iteration),
                "score": current_score,
                "rules_passed": rules_passed,
                "total_rules": total_rules,
                "improvement": (current_score - previous_scores[-1]) if previous_scores else 0,
                "validation": validation.model_dump(),
                "documents_processed": len(claim_packet.documents)
            })
            
            # EXIT CONDITIONS
            if current_score >= 0.8:
                print(f"🎉 TARGET: {current_score:.1%} ≥80%!")
                break
            
            previous_scores.append(current_score)
            
            if iteration < max_iterations:
                improvement_so_far = current_score - previous_scores[0] if len(previous_scores) > 1 else 0
                print(f"🔄 Current {current_score:.1%}, improved {improvement_so_far:+.1%} total, continuing...")
        
        final_validation = validation_history[-1]["validation"]
        
        print(f"\n🏁 COMPLETE: {final_validation['overall_score']:.1%} after {iteration} iterations")
        
        # Save to database
        from database import ClaimRecord, SessionLocal
        db = SessionLocal()
        try:
            claim_record = db.query(ClaimRecord).filter(ClaimRecord.claim_id == claim_packet.claim_id).first()
            if claim_record:
                claim_record.status = "validated"
                claim_record.validation_result = final_validation
                claim_record.updated_at = datetime.now()
                db.commit()
        except Exception as db_error:
            db.rollback()
        finally:
            db.close()
        
        return {
            "final_validation": final_validation,
            "validation_history": validation_history,
            "iterations_completed": iteration,
            "total_improvement": (previous_scores[-1] - previous_scores[0]) if len(previous_scores) > 1 else 0,
            "final_analysis_depth": ai_judge._get_depth_name(iteration),
            "next_step": "generate_final_outputs"
        }
    except Exception as e:
        print(f"❌ Validation loop error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
