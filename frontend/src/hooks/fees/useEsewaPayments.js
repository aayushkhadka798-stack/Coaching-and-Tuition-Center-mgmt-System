import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { failEsewaPayment, initiateEsewaPayment, listOnlinePayments, verifyEsewaPayment } from '../../api/esewaApi'

export const useInitiateEsewaPayment = () => useMutation({ mutationFn: ({ feeId, amount }) => initiateEsewaPayment(feeId, amount) })

export const useVerifyEsewaPayment = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: verifyEsewaPayment,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['fees'] }),
  })
}

export const useFailEsewaPayment = () => useMutation({ mutationFn: failEsewaPayment })
export const useOnlinePayments = (params) => useQuery({ queryKey: ['esewa-transactions', params], queryFn: () => listOnlinePayments(params) })
