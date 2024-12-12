from django.shortcuts import render
from django.http import JsonResponse
import threading

# Define memory block lists for Quick Fit
block_sizes = [64, 128, 256, 512]  # Predefined block sizes
free_blocks = {size: [] for size in block_sizes}  # Free block lists
allocated_blocks = {size: 0 for size in block_sizes}  # Track allocated blocks for each size
free_blocks_lock = threading.Lock()  # Lock for thread safety

# Initialize total memory blocks for demonstration
initial_memory = {size: 5 for size in block_sizes}  # 5 blocks of each size
for size in block_sizes:
    free_blocks[size] = [f"Block-{size}-{i}" for i in range(1, initial_memory[size] + 1)]


# Allocate memory function
def allocate_memory(request):
    block_size = int(request.GET.get('size', 0))  # Memory request size

    if block_size <= 0:
        return JsonResponse({"status": "failure", "message": "Invalid block size requested."})

    with free_blocks_lock:  # Ensure thread-safe operations
        # Check for an exact match
        if block_size in free_blocks and free_blocks[block_size]:
            allocated = free_blocks[block_size].pop(0)
            allocated_blocks[block_size] += 1  # Update allocated blocks count
            return JsonResponse({"status": "success", "allocated": allocated})

        # Check for the nearest larger block
        for size in sorted(free_blocks.keys()):
            if size >= block_size and free_blocks[size]:
                allocated = free_blocks[size].pop(0)
                allocated_blocks[size] += 1  # Update allocated blocks count
                return JsonResponse({"status": "success", "allocated": allocated})

        # If no suitable block is found, dynamically add a new block size
        free_blocks[block_size] = [f"Block-{block_size}-1"]
        allocated = free_blocks[block_size].pop(0)
        allocated_blocks[block_size] += 1  # Update allocated blocks count
        return JsonResponse({"status": "success", "allocated": allocated})


# Deallocate memory function
def deallocate_memory(request):
    block_size = int(request.GET.get('size', 0))  # Memory block size to deallocate
    block_name = request.GET.get('block', '')  # Memory block name

    if block_size <= 0 or not block_name:
        return JsonResponse({"status": "failure", "message": "Invalid deallocation request."})

    with free_blocks_lock:  # Ensure thread-safe operations
        if block_size in free_blocks:
            free_blocks[block_size].append(block_name)
            allocated_blocks[block_size] -= 1  # Update allocated blocks count
            return JsonResponse({"status": "success", "message": f"Block {block_name} deallocated."})

    return JsonResponse({"status": "failure", "message": "Invalid block size for deallocation."})


# View to display memory status
def memory_status(request):
    with free_blocks_lock:  # Ensure thread-safe operations
        memory_status_data = {
            "total_blocks": {size: initial_memory.get(size, 0) for size in block_sizes},
            "free_blocks": {size: len(free_blocks.get(size, [])) for size in block_sizes},
            "allocated_blocks": {
                size: allocated_blocks.get(size, 0) for size in block_sizes
            },
        }
    return JsonResponse({"status": "success", "memory_status": memory_status_data})


# View to render the memory management page
def memory_management(request):
    return render(request, 'quickfit/memory.html')
