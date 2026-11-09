# Open-source contributions

**178 merged pull requests across 29 upstream repositories.**

Updated: 2026-11-09. Scope: PRs authored by `ninglinLiu`, merged upstream, excluding repositories owned by `ninglinLiu`. Features, fixes, tests, refactoring and documentation are all included.

[Back to profile](../README.md) · [Live GitHub search](https://github.com/search?q=is%3Apr+author%3AninglinLiu+is%3Amerged+-user%3AninglinLiu&type=pullrequests)

## CrossGL/crosstl · 92 merged

| Pull request | Merged (UTC) |
|---|---|
| [#3616 — fix(wgsl): lower StructuredBuffer.length() to arrayLength](https://github.com/CrossGL/crosstl/pull/3616) | 2026-10-31 |
| [#3411 — fix(wgsl): lower struct, array and matrix conditionals to if/else instead of select](https://github.com/CrossGL/crosstl/pull/3411) | 2026-10-30 |
| [#3176 — test(cuda,hip): cover scalar length, distance and normalize on parameters](https://github.com/CrossGL/crosstl/pull/3176) | 2026-10-30 |
| [#3534 — fix(wgsl): bind gl_PrimitiveID and SV_PrimitiveID to primitive_index](https://github.com/CrossGL/crosstl/pull/3534) | 2026-10-30 |
| [#3410 — fix(cuda,hip,opencl): rename types named after CrossGL keywords on import](https://github.com/CrossGL/crosstl/pull/3410) | 2026-10-30 |
| [#3533 — fix(wgsl): write flat, noperspective, centroid and sample interpolation as @interpolate](https://github.com/CrossGL/crosstl/pull/3533) | 2026-10-30 |
| [#3409 — fix(slang): import C-style casts to array types such as (float[3])0](https://github.com/CrossGL/crosstl/pull/3409) | 2026-10-30 |
| [#3408 — fix(cuda,hip): import namespace-scope const and constexpr variables as CrossGL constants](https://github.com/CrossGL/crosstl/pull/3408) | 2026-10-30 |
| [#3407 — fix(metal): rename shader-scope constants spelled like Metal keywords](https://github.com/CrossGL/crosstl/pull/3407) | 2026-10-30 |
| [#3406 — fix(wgsl): pass the array texture layer to offset, gradient and shadow lookups](https://github.com/CrossGL/crosstl/pull/3406) | 2026-10-30 |
| [#3405 — fix(cuda,hip): run the out/inout argument checks on calls to generic functions](https://github.com/CrossGL/crosstl/pull/3405) | 2026-10-30 |
| [#3195 — fix(cuda,hip): keep the grouping of nested prefix operators](https://github.com/CrossGL/crosstl/pull/3195) | 2026-10-28 |
| [#3177 — fix(hip): keep static and const on variable declarations](https://github.com/CrossGL/crosstl/pull/3177) | 2026-10-28 |
| [#3181 — fix(cuda,hip): refuse swizzles passed to out and inout parameters](https://github.com/CrossGL/crosstl/pull/3181) | 2026-10-27 |
| [#3180 — fix(cuda,hip): lower HLSL atomics that return the original value through an argument](https://github.com/CrossGL/crosstl/pull/3180) | 2026-10-27 |
| [#3188 — test(slang): cover bare block statements with their own scope](https://github.com/CrossGL/crosstl/pull/3188) | 2026-10-27 |
| [#3182 — fix(wgsl): refuse filtered texture lookups on integer samplers](https://github.com/CrossGL/crosstl/pull/3182) | 2026-10-27 |
| [#3184 — fix(wgsl): pass the layer of array texture lookups as its own argument](https://github.com/CrossGL/crosstl/pull/3184) | 2026-10-27 |
| [#3126 — fix(cuda,hip): lower length, normalize, distance and cross on half vectors to helpers](https://github.com/CrossGL/crosstl/pull/3126) | 2026-10-27 |
| [#3179 — fix(cuda,hip,metal): keep parentheses around the operand of a postfix update](https://github.com/CrossGL/crosstl/pull/3179) | 2026-10-26 |
| [#3170 — fix(wgsl): map integer 1D, 3D and cube samplers to typed textures](https://github.com/CrossGL/crosstl/pull/3170) | 2026-10-26 |
| [#3169 — fix(wgsl): give imageSize the GLSL result shape for 1D, 3D and array images](https://github.com/CrossGL/crosstl/pull/3169) | 2026-10-26 |
| [#3158 — fix(opencl): order the memory that barrier flags name](https://github.com/CrossGL/crosstl/pull/3158) | 2026-10-26 |
| [#3157 — fix(metal): keep the common operand type for mixed vectors declared as integer vectors](https://github.com/CrossGL/crosstl/pull/3157) | 2026-10-26 |
| [#3150 — fix(metal): refuse derivatives in kernel, mesh and object functions](https://github.com/CrossGL/crosstl/pull/3150) | 2026-10-26 |
| [#3149 — fix(slang): carry the WaveSize attribute into the CrossGL entry point](https://github.com/CrossGL/crosstl/pull/3149) | 2026-10-26 |
| [#3146 — fix(wgsl): expand one-scalar matrix constructors into diagonal columns](https://github.com/CrossGL/crosstl/pull/3146) | 2026-10-26 |
| [#3145 — fix(mojo): splat a bool into a boolean vector with the fill keyword](https://github.com/CrossGL/crosstl/pull/3145) | 2026-10-26 |
| [#3123 — fix(cuda,hip): apply scalar math built-ins to half vectors through per-component helpers](https://github.com/CrossGL/crosstl/pull/3123) | 2026-10-26 |
| [#3143 — fix(directx): refuse the WaveSize attribute for the dx10 and dx11 profiles](https://github.com/CrossGL/crosstl/pull/3143) | 2026-10-26 |
| [#3120 — fix(cuda,hip): expand half vector swizzles through the half constructors](https://github.com/CrossGL/crosstl/pull/3120) | 2026-10-26 |
| [#2812 — fix(hlsl): keep the dx:: namespace on imported HitObject types](https://github.com/CrossGL/crosstl/pull/2812) | 2026-10-26 |
| [#3140 — fix(mojo): combine boolean vector masks with & and \| for && and \|\|](https://github.com/CrossGL/crosstl/pull/3140) | 2026-10-26 |
| [#3118 — fix(cuda,hip): compute half vector % and mod through the float mod helper](https://github.com/CrossGL/crosstl/pull/3118) | 2026-10-26 |
| [#3139 — fix(directx): report directx-12 only for DXR, mesh shading and wave intrinsic HLSL](https://github.com/CrossGL/crosstl/pull/3139) | 2026-10-26 |
| [#3138 — fix(directx): refuse mesh and amplification stages for the dx10 and dx11 profiles](https://github.com/CrossGL/crosstl/pull/3138) | 2026-10-26 |
| [#2818 — fix(slang): type matrix-valued expressions and lower matrix built-ins](https://github.com/CrossGL/crosstl/pull/2818) | 2026-10-26 |
| [#3133 — fix(mojo): refuse implicit vector to scalar conversions](https://github.com/CrossGL/crosstl/pull/3133) | 2026-10-26 |
| [#3130 — fix(directx): refuse ray tracing stages for the dx10 and dx11 profiles](https://github.com/CrossGL/crosstl/pull/3130) | 2026-10-26 |
| [#3129 — test(fuzz): keep float-to-integer conversions defined](https://github.com/CrossGL/crosstl/pull/3129) | 2026-10-26 |
| [#3117 — fix(cuda,hip): use vector-scalar helpers when the scalar operand is a constructor call](https://github.com/CrossGL/crosstl/pull/3117) | 2026-10-26 |
| [#3112 — fix(cuda,hip): lower half vector and half scalar arithmetic to scalar helpers](https://github.com/CrossGL/crosstl/pull/3112) | 2026-10-26 |
| [#3110 — fix(cuda,hip): splat a half vector constructor of a native half2 component](https://github.com/CrossGL/crosstl/pull/3110) | 2026-10-26 |
| [#3108 — fix(wgsl): discard the value of @must_use built-in call statements](https://github.com/CrossGL/crosstl/pull/3108) | 2026-10-25 |
| [#2996 — fix(opencl): lower atomic_sub, atomic_fetch_sub and atomic_dec to atomicAdd of the negated operand](https://github.com/CrossGL/crosstl/pull/2996) | 2026-10-25 |
| [#2993 — fix(opencl): lower read_imagef to textureLod, texelFetch and imageLoad](https://github.com/CrossGL/crosstl/pull/2993) | 2026-10-25 |
| [#3106 — fix(cuda,hip): splat a vector constructor of a scalar cast](https://github.com/CrossGL/crosstl/pull/3106) | 2026-10-25 |
| [#2988 — fix(opencl): refuse device-side enqueue event builtins for every target](https://github.com/CrossGL/crosstl/pull/2988) | 2026-10-25 |
| [#3104 — fix(cuda,hip): keep sinpi and cospi instead of refusing them](https://github.com/CrossGL/crosstl/pull/3104) | 2026-10-25 |
| [#2984 — fix(opencl): lower write_imagef, write_imagei and write_imageui to imageStore](https://github.com/CrossGL/crosstl/pull/2984) | 2026-10-25 |
| [#3103 — fix(hlsl,wgsl): accept the GLSL importer's fwidth_fine and fwidth_coarse spellings](https://github.com/CrossGL/crosstl/pull/3103) | 2026-10-25 |
| [#2977 — fix(opencl): drop prefetch hints instead of copying them into CrossGL](https://github.com/CrossGL/crosstl/pull/2977) | 2026-10-25 |
| [#2792 — fix(cuda): emit normf/rnormf for float euclidean norm arrays](https://github.com/CrossGL/crosstl/pull/2792) | 2026-10-25 |
| [#2830 — fix(cuda): lower doubleBitsToLong and longBitsToDouble to CUDA intrinsics](https://github.com/CrossGL/crosstl/pull/2830) | 2026-10-25 |
| [#2972 — fix(opencl): lower OpenCL C fences and sub_group_barrier to CrossGL fences](https://github.com/CrossGL/crosstl/pull/2972) | 2026-10-25 |
| [#2918 — fix(wgsl): lower HLSL 8-bit pack intrinsics to WGSL pack4x builtins](https://github.com/CrossGL/crosstl/pull/2918) | 2026-10-25 |
| [#2974 — fix(mojo): do not lower comptime DType aliases to CrossGL globals](https://github.com/CrossGL/crosstl/pull/2974) | 2026-10-25 |
| [#2935 — fix(metal): lower fine and coarse derivatives to dfdx, dfdy and fwidth](https://github.com/CrossGL/crosstl/pull/2935) | 2026-10-25 |
| [#2963 — fix(metal): import make_filled_matrix as a matrix of column splats](https://github.com/CrossGL/crosstl/pull/2963) | 2026-10-25 |
| [#2979 — fix(hip): lower doubleBitsToLong and longBitsToDouble to HIP intrinsics](https://github.com/CrossGL/crosstl/pull/2979) | 2026-10-25 |
| [#2954 — fix(wgsl): give Slang SV_Target results a location](https://github.com/CrossGL/crosstl/pull/2954) | 2026-10-25 |
| [#2931 — fix(metal): lower HLSL 8-bit pack intrinsics to byte vectors and as_type](https://github.com/CrossGL/crosstl/pull/2931) | 2026-10-25 |
| [#3008 — fix(hip): lower countLeadingZeros to __clz and __clzll](https://github.com/CrossGL/crosstl/pull/3008) | 2026-10-25 |
| [#2945 — test(hlsl): check column subscripts of matrixCompMult and outerProduct results](https://github.com/CrossGL/crosstl/pull/2945) | 2026-10-25 |
| [#2927 — fix(metal): lower dot4add_i8packed and dot4add_u8packed to lane dot products](https://github.com/CrossGL/crosstl/pull/2927) | 2026-10-25 |
| [#3025 — fix(wgsl): lower two-argument atan to atan2](https://github.com/CrossGL/crosstl/pull/3025) | 2026-10-25 |
| [#3018 — fix(wgsl): return signed textureSize results and add array layer counts](https://github.com/CrossGL/crosstl/pull/3018) | 2026-10-25 |
| [#2999 — fix(cuda): lower countLeadingZeros to __clz and __clzll](https://github.com/CrossGL/crosstl/pull/2999) | 2026-10-25 |
| [#2966 — fix(opencl): drop relaxed explicit atomic orders and refuse the rest](https://github.com/CrossGL/crosstl/pull/2966) | 2026-10-25 |
| [#2955 — fix(hlsl): refuse inout SV_Position vertex parameters outside HLSL](https://github.com/CrossGL/crosstl/pull/2955) | 2026-10-25 |
| [#2948 — fix(slang): map @builtin(...) parameters to system values and bind gl_NumWorkGroups from WorkgroupCount()](https://github.com/CrossGL/crosstl/pull/2948) | 2026-10-25 |
| [#2923 — fix(glsl): lower HLSL 8-bit pack intrinsics to packUnorm4x8 and lane shifts](https://github.com/CrossGL/crosstl/pull/2923) | 2026-10-25 |
| [#3029 — fix(hlsl): lower gl_HelperInvocation to IsHelperLane()](https://github.com/CrossGL/crosstl/pull/3029) | 2026-10-25 |
| [#3015 — fix(wgsl): lower mix with a boolean selector to select](https://github.com/CrossGL/crosstl/pull/3015) | 2026-10-25 |
| [#2890 — fix(slang): map GLSL 8-bit and 64-bit integer spellings to Slang types](https://github.com/CrossGL/crosstl/pull/2890) | 2026-10-25 |
| [#2998 — fix(cuda): include <cstdint> so fixed-width integer types are declared](https://github.com/CrossGL/crosstl/pull/2998) | 2026-10-25 |
| [#2876 — fix(slang): lower fwidthCoarse and fwidthFine to fwidth_coarse and fwidth_fine](https://github.com/CrossGL/crosstl/pull/2876) | 2026-10-25 |
| [#2919 — fix(glsl): lower dot4add_i8packed and dot4add_u8packed to lane dot products](https://github.com/CrossGL/crosstl/pull/2919) | 2026-10-25 |
| [#2964 — fix(opencl): import get_local_linear_id() as the local invocation index](https://github.com/CrossGL/crosstl/pull/2964) | 2026-10-25 |
| [#2797 — fix(slang): map HLSL barrier intrinsics like the HLSL importer](https://github.com/CrossGL/crosstl/pull/2797) | 2026-10-25 |
| [#2802 — fix(slang): map int8_t4_packed and uint8_t4_packed to uint](https://github.com/CrossGL/crosstl/pull/2802) | 2026-10-25 |
| [#2856 — fix(slang): map GLSL 16-bit integer spellings to Slang types](https://github.com/CrossGL/crosstl/pull/2856) | 2026-10-25 |
| [#2913 — fix(wgsl): lower dot4add_i8packed and dot4add_u8packed to packed dot products](https://github.com/CrossGL/crosstl/pull/2913) | 2026-10-24 |
| [#2904 — fix(wgsl): lower memory barriers to WGSL workgroup, storage and texture barriers](https://github.com/CrossGL/crosstl/pull/2904) | 2026-10-24 |
| [#2900 — fix(wgsl): lower matrix-scalar arithmetic, matrixCompMult and outerProduct by column](https://github.com/CrossGL/crosstl/pull/2900) | 2026-10-24 |
| [#2895 — fix(hlsl): lower fwidthFine and fwidthCoarse to fine and coarse derivatives](https://github.com/CrossGL/crosstl/pull/2895) | 2026-10-24 |
| [#2891 — fix(hlsl): map packed 8-bit aliases in structured buffer element types](https://github.com/CrossGL/crosstl/pull/2891) | 2026-10-24 |
| [#2881 — fix(slang): lower gl_NumWorkGroups to WorkgroupCount() in compute shaders](https://github.com/CrossGL/crosstl/pull/2881) | 2026-10-24 |
| [#2790 — fix(slang): keep groupshared on imported globals](https://github.com/CrossGL/crosstl/pull/2790) | 2026-10-24 |
| [#2780 — fix(slang): match HLSL matrix orientation for constructors and types](https://github.com/CrossGL/crosstl/pull/2780) | 2026-10-24 |
| [#2791 — fix(wgsl): pass workgroup pointer to workgroupUniformLoad](https://github.com/CrossGL/crosstl/pull/2791) | 2026-10-24 |
| [#2751 — docs: close Sphinx inline literal in private_global_prefix docstring](https://github.com/CrossGL/crosstl/pull/2751) | 2026-10-23 |

## kyegomez/swarms · 12 merged

| Pull request | Merged (UTC) |
|---|---|
| [#2982 — [DOCS][MixtureOfAgents][Document id as the telemetry instance identifier]](https://github.com/kyegomez/swarms/pull/2982) | 2026-10-29 |
| [#2981 — [REFACTOR][Agent.run][Remove the n parameter]](https://github.com/kyegomez/swarms/pull/2981) | 2026-10-29 |
| [#2980 — [DOCS][HeavySwarm][Drop the removed agents parameter from the docstring]](https://github.com/kyegomez/swarms/pull/2980) | 2026-10-29 |
| [#2966 — [FIX][Agent._handle_run_error][Log provider errors without str.format on braces]](https://github.com/kyegomez/swarms/pull/2966) | 2026-10-29 |
| [#2978 — [DOCS][CLAUDE.md][Show PlannerWorkerSwarm(agents=, planner_model_name=)]](https://github.com/kyegomez/swarms/pull/2978) | 2026-10-28 |
| [#2965 — [PERF][Conversation][Import yaml inside the methods that use it]](https://github.com/kyegomez/swarms/pull/2965) | 2026-10-28 |
| [#2911 — [REFACTOR][AgentRearrange][Remove the unread memory_system parameter]](https://github.com/kyegomez/swarms/pull/2911) | 2026-10-27 |
| [#2918 — [REFACTOR][GroupChat][Remove the deprecated idle_timeout parameter]](https://github.com/kyegomez/swarms/pull/2918) | 2026-10-27 |
| [#2920 — [REFACTOR][Agent.run][Remove the unused correct_answer parameter]](https://github.com/kyegomez/swarms/pull/2920) | 2026-10-27 |
| [#2912 — [REFACTOR][SequentialWorkflow][Remove the unread shared_memory_system parameter]](https://github.com/kyegomez/swarms/pull/2912) | 2026-10-27 |
| [#2917 — [REFACTOR][MultiAgentRouter][Remove the unread shared_memory_system parameter]](https://github.com/kyegomez/swarms/pull/2917) | 2026-10-27 |
| [#2891 — chore(agent): remove unused Agent.check_available_tokens](https://github.com/kyegomez/swarms/pull/2891) | 2026-10-26 |

## foundry-rs/foundry-core · 8 merged

| Pull request | Merged (UTC) |
|---|---|
| [#279 — fix(artifacts): keep a context's trailing slash when displaying remappings on Windows](https://github.com/foundry-rs/foundry-core/pull/279) | 2026-10-27 |
| [#276 — test(explorers): use a still-unverified address in the mainnet verify test](https://github.com/foundry-rs/foundry-core/pull/276) | 2026-10-27 |
| [#283 — fix(explorers): return ParseOverflow instead of wrapping or panicking in parse_units](https://github.com/foundry-rs/foundry-core/pull/283) | 2026-10-27 |
| [#282 — fix(explorers): reject negative and oversized integers when converting to Units](https://github.com/foundry-rs/foundry-core/pull/282) | 2026-10-27 |
| [#284 — fix(explorers): return an error for a malformed getblocknobytime result instead of panicking](https://github.com/foundry-rs/foundry-core/pull/284) | 2026-10-27 |
| [#285 — fix(explorers): don't panic on a cache TTL that overflows](https://github.com/foundry-rs/foundry-core/pull/285) | 2026-10-27 |
| [#274 — fix(compilers): store cached remappings root-relative](https://github.com/foundry-rs/foundry-core/pull/274) | 2026-10-26 |
| [#275 — chore(deps): bump crypto-bigint to 0.7.10 for RUSTSEC-2026-0387](https://github.com/foundry-rs/foundry-core/pull/275) | 2026-10-26 |

## microsoft/agent-framework · 8 merged

| Pull request | Merged (UTC) |
|---|---|
| [#10108 — .NET: docs: fix dont typos in ChatCompletions comments](https://github.com/microsoft/agent-framework/pull/10108) | 2026-11-05 |
| [#10070 — docs: fix spelling typos in decision records](https://github.com/microsoft/agent-framework/pull/10070) | 2026-11-04 |
| [#9873 — .NET: fall back when a restored agent mode is no longer configured](https://github.com/microsoft/agent-framework/pull/9873) | 2026-11-02 |
| [#9781 — Python: use FOUNDRY_* settings in the red teaming sample README](https://github.com/microsoft/agent-framework/pull/9781) | 2026-11-02 |
| [#9758 — Python: use FOUNDRY_* settings in the ChatKit integration sample README](https://github.com/microsoft/agent-framework/pull/9758) | 2026-11-02 |
| [#9740 — Python: use FOUNDRY_MODEL in the Content Understanding DevUI sample READMEs](https://github.com/microsoft/agent-framework/pull/9740) | 2026-11-02 |
| [#9859 — Python: include Anthropic cache tokens in input_token_count](https://github.com/microsoft/agent-framework/pull/9859) | 2026-11-02 |
| [#9741 — Python: use AZURE_OPENAI_EMBEDDING_MODEL in the Foundry memory sample README](https://github.com/microsoft/agent-framework/pull/9741) | 2026-10-27 |

## 567-labs/instructor · 6 merged

| Pull request | Merged (UTC) |
|---|---|
| [#2789 — docs(tutorials): stop teaching instructor.patch() as the core path](https://github.com/567-labs/instructor/pull/2789) | 2026-11-03 |
| [#2788 — docs(tutorials): fix OpenAI().create(...) in 1-introduction.ipynb](https://github.com/567-labs/instructor/pull/2788) | 2026-11-03 |
| [#2794 — docs(llms.txt): fix Maybe factory and result/error/message fields](https://github.com/567-labs/instructor/pull/2794) | 2026-11-03 |
| [#2793 — docs(partial): stop requiring deprecated PartialLiteralMixin](https://github.com/567-labs/instructor/pull/2793) | 2026-11-03 |
| [#2786 — docs(blog): drop non-existent RedisCache from native caching callout](https://github.com/567-labs/instructor/pull/2786) | 2026-11-03 |
| [#2785 — docs(anthropic): fix PdfWithCacheControl → PDFWithCacheControl](https://github.com/567-labs/instructor/pull/2785) | 2026-11-03 |

## livekit/client-sdk-js · 6 merged

| Pull request | Merged (UTC) |
|---|---|
| [#2237 — docs: fix withing typo in WrapAroundUnsignedInt comment](https://github.com/livekit/client-sdk-js/pull/2237) | 2026-11-06 |
| [#2198 — fix(token-source): don't return the cached response for options whose fetch failed](https://github.com/livekit/client-sdk-js/pull/2198) | 2026-10-27 |
| [#2188 — fix(e2ee): decrypt data packets with the ratcheted key when retrying](https://github.com/livekit/client-sdk-js/pull/2188) | 2026-10-27 |
| [#2196 — fix(engine): ignore the mid mapping of a stale publisher answer](https://github.com/livekit/client-sdk-js/pull/2196) | 2026-10-27 |
| [#2189 — fix(engine): apply peerConnectionTimeout to the negotiation deadline](https://github.com/livekit/client-sdk-js/pull/2189) | 2026-10-26 |
| [#2192 — fix(signal): don't log a requested signal close as a read error](https://github.com/livekit/client-sdk-js/pull/2192) | 2026-10-26 |

## pipecat-ai/pipecat · 6 merged

| Pull request | Merged (UTC) |
|---|---|
| [#6413 — fix(openai-live): chunk Chinese and Japanese context appends at sentence endings](https://github.com/pipecat-ai/pipecat/pull/6413) | 2026-11-03 |
| [#6405 — fix(turns): match Chinese and Japanese wake phrases inside unspaced transcripts](https://github.com/pipecat-ai/pipecat/pull/6405) | 2026-11-03 |
| [#6411 — fix(utils): keep exact microseconds in nanoseconds_to_str](https://github.com/pipecat-ai/pipecat/pull/6411) | 2026-10-28 |
| [#6398 — Fix dead LiveAvatar sandbox and SageMaker deployment links in examples](https://github.com/pipecat-ai/pipecat/pull/6398) | 2026-10-27 |
| [#6389 — Fix the Gradium key name and drop removed services in env.example](https://github.com/pipecat-ai/pipecat/pull/6389) | 2026-10-27 |
| [#6387 — Fix the 404 Pipecat Cloud docs link printed by pipecat init](https://github.com/pipecat-ai/pipecat/pull/6387) | 2026-10-27 |

## foundry-rs/foundry · 4 merged

| Pull request | Merged (UTC) |
|---|---|
| [#18097 — docs: fix dont typos in fmt dynamic comments](https://github.com/foundry-rs/foundry/pull/18097) | 2026-11-04 |
| [#17926 — fix(cast): hint when a trailing flag is eaten as an ABI encode arg](https://github.com/foundry-rs/foundry/pull/17926) | 2026-11-03 |
| [#17925 — fix(cast): keep decode-error/event --json stdout as JSON only](https://github.com/foundry-rs/foundry/pull/17925) | 2026-11-02 |
| [#17933 — fix(forge): defer DTL-disable warning until compile succeeds](https://github.com/foundry-rs/foundry/pull/17933) | 2026-10-30 |

## livekit/agents · 4 merged

| Pull request | Merged (UTC) |
|---|---|
| [#8270 — fix(tools): omit cancel_task from duplicate reject/confirm when not cancellable](https://github.com/livekit/agents/pull/8270) | 2026-11-02 |
| [#8151 — docs(plugins): fix environment variables in the neuphonic and rtzr READMEs](https://github.com/livekit/agents/pull/8151) | 2026-10-27 |
| [#8093 — fix(worker): return 503 from health until RegisterWorkerResponse](https://github.com/livekit/agents/pull/8093) | 2026-10-25 |
| [#7891 — fix(google): count Gemini thinking tokens in LLM completion_tokens](https://github.com/livekit/agents/pull/7891) | 2026-10-25 |

## livekit/components-js · 4 merged

| Pull request | Merged (UTC) |
|---|---|
| [#1506 — docs: fix overriden typo in IYamlApiFile comment](https://github.com/livekit/components-js/pull/1506) | 2026-11-08 |
| [#1503 — docs: fix controling/visualing typos in Agents UI README](https://github.com/livekit/components-js/pull/1503) | 2026-11-04 |
| [#1498 — docs: remove duplicated word in README examples note](https://github.com/livekit/components-js/pull/1498) | 2026-11-03 |
| [#1479 — refactor(react): use areTokenSourceFetchOptionsEqual from livekit-client in useSession](https://github.com/livekit/components-js/pull/1479) | 2026-10-27 |

## NonceGeek/dim-sum-right-proof · 3 merged

| Pull request | Merged (UTC) |
|---|---|
| [#8 — Feat/sync main architecture](https://github.com/NonceGeek/dim-sum-right-proof/pull/8) | 2025-10-19 |
| [#7 — chore: Align with main architecture after leeduckgo's merge](https://github.com/NonceGeek/dim-sum-right-proof/pull/7) | 2025-10-18 |
| [#6 — Feat: Update verified BodhiBasedCopyright Holesky deployment & DApp integration](https://github.com/NonceGeek/dim-sum-right-proof/pull/6) | 2025-10-18 |

## ag2ai/ag2 · 3 merged

| Pull request | Merged (UTC) |
|---|---|
| [#3516 — fix(acp,mcp): preserve explicitly provided empty session storage](https://github.com/ag2ai/ag2/pull/3516) | 2026-10-31 |
| [#3521 — docs: drop dead notebook links and the orphaned MCP client snippet](https://github.com/ag2ai/ag2/pull/3521) | 2026-10-28 |
| [#3519 — feat(anthropic): expose the SDK's open_telemetry option on AnthropicConfig](https://github.com/ag2ai/ag2/pull/3519) | 2026-10-27 |

## apache/arrow-rs · 3 merged

| Pull request | Merged (UTC) |
|---|---|
| [#11925 — fix(arrow-select): merge dictionaries in merge and merge_n instead of panicking on key overflow](https://github.com/apache/arrow-rs/pull/11925) | 2026-10-28 |
| [#11915 — fix(arrow-avro): keep nulls when reading strings as Utf8View](https://github.com/apache/arrow-rs/pull/11915) | 2026-10-26 |
| [#11906 — fix(arrow-data): extend Interval(DayTime) as IntervalDayTime in MutableArrayData](https://github.com/apache/arrow-rs/pull/11906) | 2026-10-26 |

## apache/iceberg-rust · 2 merged

| Pull request | Merged (UTC) |
|---|---|
| [#3553 — chore(release): check crate LICENSE/NOTICE files in verify_rc.sh](https://github.com/apache/iceberg-rust/pull/3553) | 2026-10-27 |
| [#3528 — chore(dev): fold the crate LICENSE/NOTICE check into licenses.py](https://github.com/apache/iceberg-rust/pull/3528) | 2026-10-27 |

## browser-use/browser-use · 2 merged

| Pull request | Merged (UTC) |
|---|---|
| [#6052 — docs(skills): update browser-hour price $0.05 → $0.02](https://github.com/browser-use/browser-use/pull/6052) | 2026-10-17 |
| [#6051 — docs(skills): align signup credit with live pricing ($15 → $1)](https://github.com/browser-use/browser-use/pull/6051) | 2026-10-17 |

## pydantic/pydantic-ai · 2 merged

| Pull request | Merged (UTC) |
|---|---|
| [#10230 — Use the `result.usage` property in the `ModelResponse.usage` docstring](https://github.com/pydantic/pydantic-ai/pull/10230) | 2026-10-15 |
| [#10171 — Use the `result.usage` property in the `SystemReminders` docs](https://github.com/pydantic/pydantic-ai/pull/10171) | 2026-10-13 |

## BerriAI/litellm · 1 merged

| Pull request | Merged (UTC) |
|---|---|
| [#46171 — fix: correct Palm 'decommissioned' typo in error message](https://github.com/BerriAI/litellm/pull/46171) | 2026-10-27 |

## Leaflet/Leaflet · 1 merged

| Pull request | Merged (UTC) |
|---|---|
| [#10543 — docs: fix allready typo in ImageOverlay spec](https://github.com/Leaflet/Leaflet/pull/10543) | 2026-11-08 |

## NethermindEth/nethermind · 1 merged

| Pull request | Merged (UTC) |
|---|---|
| [#15734 — docs: remove duplicated words in comments and StatsAnalyzer docs](https://github.com/NethermindEth/nethermind/pull/15734) | 2026-11-09 |

## OpenZeppelin/openzeppelin-monitor · 1 merged

| Pull request | Merged (UTC) |
|---|---|
| [#526 — test: add a shared MonitorMatch test builder](https://github.com/OpenZeppelin/openzeppelin-monitor/pull/526) | 2026-10-28 |

## apache/datafusion · 1 merged

| Pull request | Merged (UTC) |
|---|---|
| [#26681 — chore(csv): use shared aggr_test_schema in CSV scan tests](https://github.com/apache/datafusion/pull/26681) | 2026-10-24 |

## biomejs/biome · 1 merged

| Pull request | Merged (UTC) |
|---|---|
| [#13039 — docs: remove duplicated word in HTML formatter debug comment](https://github.com/biomejs/biome/pull/13039) | 2026-11-09 |

## foundry-rs/book · 1 merged

| Pull request | Merged (UTC) |
|---|---|
| [#2196 — docs(tempo): fix dead TIP-1049 link](https://github.com/foundry-rs/book/pull/2196) | 2026-10-27 |

## microsoft/onnxruntime · 1 merged

| Pull request | Merged (UTC) |
|---|---|
| [#33532 — fix: scope tpause_spin_delay_cycles to the _tpause branch](https://github.com/microsoft/onnxruntime/pull/33532) | 2026-10-22 |

## pipecat-ai/docs · 1 merged

| Pull request | Merged (UTC) |
|---|---|
| [#1599 — docs: fix dead links to moved examples and external docs](https://github.com/pipecat-ai/docs/pull/1599) | 2026-10-27 |

## pipecat-ai/pipecat-examples · 1 merged

| Pull request | Merged (UTC) |
|---|---|
| [#260 — docs: fix dead links in the audio recording, PSTN server and P2P READMEs](https://github.com/pipecat-ai/pipecat-examples/pull/260) | 2026-10-27 |

## preactjs/preact · 1 merged

| Pull request | Merged (UTC) |
|---|---|
| [#5355 — docs: fix duplicated words and initial-letter typo](https://github.com/preactjs/preact/pull/5355) | 2026-11-08 |

## pydantic/pydantic · 1 merged

| Pull request | Merged (UTC) |
|---|---|
| [#14226 — Fix typo in `ErrorTypeDefaults` comment](https://github.com/pydantic/pydantic/pull/14226) | 2026-11-06 |

## topoteretes/cognee · 1 merged

| Pull request | Merged (UTC) |
|---|---|
| [#6266 — docs(ollama): add self-hosted Ollama and OpenAI-compatible setup](https://github.com/topoteretes/cognee/pull/6266) | 2026-10-23 |
